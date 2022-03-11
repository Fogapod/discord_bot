from __future__ import annotations

import asyncio
import logging
import os
import re
import time
import traceback

from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Type, Union

import aiohttp
import discord
import edgedb
import sentry_sdk

from discord.ext import commands  # type: ignore[attr-defined]

from .constants import PREFIX
from .context import Context

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
        await ctx.bot.edb.query(
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
        await ctx.bot.edb.query(
            """
            DELETE Prefix
            FILTER .guild_id = <snowflake>$guild_id
            """,
            guild_id=ctx.guild.id,
        )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} prefix={self.prefix}>"


class PINK(commands.Bot):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            command_prefix=PREFIX,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
            intents=discord.Intents(
                guilds=True,
                members=True,
                bans=True,
                emojis=True,
                messages=True,
                message_content=True,
                reactions=True,
            ),
            **kwargs,
        )

        self._default_prefix_re: Optional[re.Pattern[str]] = None

        self.prefixes: Dict[int, Prefix] = {}
        self.owner_ids: Set[int] = set()

        self.loop.run_until_complete(self.pre_setup())
        self.loop.create_task(self._setup())

    # --- custon functions ---
    async def pre_setup(self) -> None:
        """
        First async initialization. Critical bot components must be created here if possible
        (happens before gateway connection)
        """
        self.launched_at = time.monotonic()

        self.session = aiohttp.ClientSession(headers={"user-agent": "PINK bot"})
        self.edb = await edgedb.create_async_pool(
            dsn=os.environ["EDGEDB_DSN"],
            min_size=1,
            max_size=2,
        )  # type: ignore[no-untyped-call]

    async def _setup(self) -> None:
        await self.wait_until_ready()

        try:
            await asyncio.shield(self.setup())
        except Exception:
            await self.close()

            raise

    async def setup(self) -> None:
        """Hapens after bot is ready and does not block anything. Misc setup like filling caches"""

        await self.wait_until_ready()

        await self._get_prefixes()
        await self._fetch_owners()

        self._load_cogs()

    async def _get_prefixes(self) -> None:
        self._default_prefix_re = mention_or_prefix_regex(self.user.id, PREFIX)

        for guild in await self.edb.query(
            """
            SELECT Prefix {
                guild_id,
                prefix,
            }
            """
        ):
            self.prefixes[guild.guild_id] = Prefix.from_edb(self, guild)

    async def _fetch_owners(self) -> None:
        app_info = await self.application_info()
        if app_info.team is None:
            self.owner_ids = set((app_info.owner.id,))
        else:
            self.owner_ids = set(m.id for m in app_info.team.members)

    def _load_cogs(self) -> None:
        for cog_path in self._iterate_cogs(Path("pink") / "cogs"):
            module = ".".join(cog_path.parts)
            try:
                self.load_extension(module)
            except Exception as e:
                log.error(f"Error loading {module}: {type(e).__name__} - {e}")
                traceback.print_exc()
            else:
                print(f"loaded {module}")

    def _iterate_cogs(self, path: Path) -> Iterator[Path]:
        for entry in path.iterdir():
            if entry.name.startswith("_"):
                continue

            if entry.is_dir():
                # if folder has __init__.py, it is a cog. otherwise it is a group of cogs
                if (entry / "__init__.py").exists():
                    yield entry
                else:
                    yield from self._iterate_cogs(entry)
            else:
                yield entry.parent / entry.stem

    # --- overloads ---
    async def close(self) -> None:
        await self.edb.aclose()
        await self.session.close()

        await super().close()

    async def get_prefix(self, message: discord.Message) -> Union[List[str], str]:
        if self._default_prefix_re is None:
            # prefixes are not initialized
            return []

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
        print(f"Logged in as {self.user}!")
        print(f"Prefix: {PREFIX}")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        sentry_sdk.set_user({"id": message.author.id, "username": str(message.author)})
        sentry_sdk.set_context("channel", {"id": message.channel.id})
        sentry_sdk.set_context("guild", {"id": None if message.guild is None else message.guild.id})

        await self.process_commands(message)

    async def on_command_error(self, _: Context, _e: BaseException) -> None:
        pass
