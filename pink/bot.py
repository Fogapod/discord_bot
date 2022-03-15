from __future__ import annotations

import asyncio
import logging
import re
import time

from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Type, Union

import aiohttp
import discord
import edgedb
import sentry_sdk

from discord.ext import commands  # type: ignore[attr-defined]

from .context import Context
from .settings import settings

log = logging.getLogger(__name__)


def mention_or_prefix_regex(user_id: int, prefix: str) -> re.Pattern[str]:
    choices = [re.escape(prefix), rf"<@!?{user_id}>"]

    return re.compile(rf"(?:{'|'.join(choices)})\s*", re.I)


class Prefix:
    __slots__ = (
        "prefix",
        "prefix_re",
    )

    def __init__(self, bot: PINK, *, prefix: str):
        self.prefix = prefix

        # custom prefix or mention
        # this way prefix logic is simplified and it hopefully runs faster at a cost of
        # storing duplicate mention regexes
        self.prefix_re = mention_or_prefix_regex(bot.user.id, self.prefix)

    @classmethod
    def from_edb(cls, bot: PINK, data: edgedb.Object) -> Prefix:
        return cls(bot, prefix=data.prefix)

    async def write(self, ctx: Context) -> None:
        await ctx.bot.edb.query(  # type: ignore[no-untyped-call]
            """
            INSERT Prefix {
                guild_id := <snowflake>$guild_id,
                prefix := <str>$prefix,
            } UNLESS CONFLICT ON .guild_id
            ELSE (
                UPDATE Prefix
                SET {
                    prefix := <str>$prefix,
                }
            )
            """,
            guild_id=ctx.guild.id,
            prefix=self.prefix,
        )

    @staticmethod
    async def delete(ctx: Context) -> None:
        await ctx.bot.edb.query(  # type: ignore[no-untyped-call]
            """
            DELETE Prefix
            FILTER .guild_id = <snowflake>$guild_id
            """,
            guild_id=ctx.guild.id,
        )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} prefix={self.prefix}>"


class PINK(commands.Bot):
    def __init__(self, *, session: aiohttp.ClientSession, edb: edgedb.AsyncIOPool, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.session = session
        self.edb = edb

        self.prefixes: Dict[int, Prefix] = {}
        self.owner_ids: Set[int] = set()

    # --- overloads ---
    async def setup_hook(self) -> None:
        self.launched_at = time.monotonic()

        await self._load_prefixes()

        await self._load_cogs()

        asyncio.gather(
            self._fetch_owners(),
        )

    async def _load_prefixes(self) -> None:
        self._default_prefix_re = mention_or_prefix_regex(self.user.id, settings.PREFIX)

        for guild in await self.edb.query(  # type: ignore[no-untyped-call]
            """
            SELECT Prefix {
                guild_id,
                prefix,
            }
            """
        ):
            self.prefixes[guild.guild_id] = Prefix.from_edb(self, guild)

    async def _fetch_owners(self) -> None:
        owners = settings.OWNERS.copy()

        if settings.OWNERS_MODE == "combine":
            owners = settings.OWNERS

            app_info = await self.application_info()
            if team := app_info.team:
                owners |= set(m.id for m in team.members)
            else:
                owners.add(app_info.owner.id)

        self.owner_ids = owners

        log.info(f"bot owners: {' | '.join(map(str, self.owner_ids))}")

    async def _load_cogs(self) -> None:
        for module in self._iterate_cogs(Path("pink") / "cogs"):
            try:
                await self.load_extension(module)
            except Exception:
                log.exception(f"loading {module}")
            else:
                log.info(f"loaded {module}")

    def _iterate_cogs(self, path: Path) -> Iterator[str]:
        """
        There are 3 ways to declare cogs under cogs/ derectory:
            - name.py           : file must have setup function
            - name/__init__.py  : file must have setup function
            - group/[recursive] : must not have __init__.py file. all folders/files are treated as cogs

        Ignores paths starting with `_` and `.`.

        Returns module names for current folder and subfolders.
        """

        def to_module(path: Path) -> str:
            return ".".join(path.parts)

        for entry in path.iterdir():
            if entry.name.startswith(("_", ".")):
                continue

            if entry.is_dir():
                # if folder has __init__.py, it is a cog. otherwise it is a group of cogs
                if (entry / "__init__.py").exists():
                    yield to_module(entry)
                else:
                    yield from self._iterate_cogs(entry)
            else:
                yield to_module(entry.parent / entry.stem)

    async def get_prefix(self, message: discord.Message) -> Union[List[str], str]:
        guild_id = getattr(message.guild, "id", -1)

        if settings := self.prefixes.get(guild_id):
            prefix_re = settings.prefix_re
        else:
            prefix_re = self._default_prefix_re

        if match := prefix_re.match(message.content):
            return match[0]

        if message.guild:
            return []

        # allow empty match in DMs
        return ""

    async def get_context(
        self,
        message: discord.Message,
        *,
        cls: Optional[Type[commands.Context]] = None,
    ) -> Context:
        return await super().get_context(message, cls=cls or Context)

    # --- events ---
    async def on_ready(self) -> None:
        log.info(f"READY as {self.user}[{self.user.id}] with prefix {settings.PREFIX}")

    async def on_message(self, message: discord.Message) -> None:
        # TODO: how to make this optional? sentry must not be a hard dependency
        sentry_sdk.set_user({"id": message.author.id, "username": str(message.author)})
        sentry_sdk.set_context("channel", {"id": message.channel.id})
        sentry_sdk.set_context("guild", {"id": None if message.guild is None else message.guild.id})

        await self.process_commands(message)
