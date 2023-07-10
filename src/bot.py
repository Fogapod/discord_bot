from __future__ import annotations

import asyncio
import logging
import re
import time

from collections.abc import Iterator
from pathlib import Path
from typing import Any, Optional

import aiohttp
import asyncpg
import discord
import sentry_sdk

from discord.ext import commands

from src.context import Context
from src.settings import settings
from src.version import Version

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
        self.prefix_re = mention_or_prefix_regex(bot.user.id, self.prefix)  # type: ignore

    @classmethod
    def from_pg(cls, bot: PINK, data: asyncpg.Record) -> Prefix:
        return cls(bot, prefix=data["prefix"])

    async def write(self, ctx: Context) -> None:
        await ctx.pg.fetchrow(
            "INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2) "
            "ON CONFLICT (guild_id) DO UPDATE "
            "SET prefix = EXCLUDED.prefix",
            ctx.guild.id,  # type: ignore
            self.prefix,
        )

    @staticmethod
    async def delete(ctx: Context) -> None:
        await ctx.pg.fetchrow("DELETE FROM prefixes WHERE guild_id = $1", ctx.guild.id)  # type: ignore

    def __repr__(self) -> str:
        return f"<{type(self).__name__} prefix={self.prefix}>"


class PINK(commands.Bot):
    def __init__(
        self,
        *,
        session: aiohttp.ClientSession,
        pg: asyncpg.Pool[asyncpg.Record],
        version: Version,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.session = session
        self.pg = pg
        self.version = version

        self.prefixes: dict[int, Prefix] = {}
        self.owner_ids: set[int] = set()

    # --- overloads ---
    async def setup_hook(self) -> None:
        self.launched_at = time.monotonic()

        await self._load_prefixes()

        await self._load_cogs()

        asyncio.gather(
            self._fetch_owners(),
        )

    async def _load_prefixes(self) -> None:
        self._default_prefix_re = mention_or_prefix_regex(self.user.id, settings.bot.prefix)  # type: ignore

        for guild in await self.pg.fetch("SELECT guild_id, prefix FROM prefixes"):
            self.prefixes[guild["guild_id"]] = Prefix.from_pg(self, guild)

    async def _fetch_owners(self) -> None:
        owners = settings.owners.ids.copy()

        if settings.owners.mode == "combine":
            owners = settings.owners.ids

            app_info = await self.application_info()
            if team := app_info.team:
                owners |= {m.id for m in team.members}
            else:
                owners.add(app_info.owner.id)

        self.owner_ids = owners

        log.info("bot owners: %s", " | ".join(map(str, self.owner_ids)))

    async def _load_cogs(self) -> None:
        for module in self._iterate_cogs():
            try:
                await self.load_extension(module)
            except Exception:
                log.exception("while loading %s", module)

    def _iterate_cogs(self, path: Optional[Path] = None) -> Iterator[str]:
        """
        There are 3 ways to declare cogs under cogs/ derectory:
            - name.py           : file must have setup function
            - name/__init__.py  : file must have setup function
            - group/[recursive] : must not have __init__.py file. all folders/files are treated as cogs

        Ignores paths starting with `_` and `.`.

        Returns module names for current folder and subfolders.
        """

        if path is None:
            path = Path("src") / "cogs"

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

    async def get_prefix(self, message: discord.Message) -> list[str] | str:
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

    async def is_owner(self, user: discord.abc.User, /) -> bool:
        """Just self.owner_ids. No fancy tricks with app info fetching"""

        return user.id in self.owner_ids

    async def get_context(
        self,
        origin: discord.Message | discord.Interaction[Any],
        /,
        *,
        cls: type[commands.Context[PINK]] = discord.utils.MISSING,
    ) -> Any:
        return await super().get_context(origin, cls=cls or Context)

    async def load_extension(self, name: str, *, package: Optional[str] = None) -> None:
        log.debug("loading %s", name)

        await super().load_extension(name, package=package)

        log.info("loaded %s", name)

    async def unload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        log.debug("unloading %s", name)

        await super().unload_extension(name, package=package)

        log.info("unloaded %s", name)

    async def reload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        log.debug("reloading %s", name)

        await super().reload_extension(name, package=package)

        log.info("reloaded %s")

    # --- events ---
    async def on_ready(self) -> None:
        log.info("READY as %s (%s) with prefix %s", self.user, self.user.id, self.bot.prefix)  # type: ignore

    async def on_message(self, message: discord.Message) -> None:
        # TODO: how to make this optional? sentry must not be a hard dependency
        sentry_sdk.set_user({"id": message.author.id, "username": str(message.author)})
        sentry_sdk.set_context("channel", {"id": message.channel.id})
        sentry_sdk.set_context("guild", {"id": None if message.guild is None else message.guild.id})

        await self.process_commands(message)

    # --- custom functions ---
    async def maybe_get_user(self, user_id: int) -> Optional[discord.User]:
        """Tries to get user from cache or fetch if not present. Is not cached"""

        if user := self.get_user(user_id):
            return user

        try:
            return await self.fetch_user(user_id)
        except discord.NotFound:
            return None
