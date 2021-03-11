from __future__ import annotations

import os
import re
import logging
import traceback

from typing import Any, Set, Dict, List, Type, Union, Optional

import edgedb
import aiohttp
import discord
import sentry_sdk

from discord.ext import commands

from .context import Context
from .constants import PREFIX

log = logging.getLogger(__name__)

initial_extensions = (
    "potato_bot.cogs.utils.errorhandler",
    "potato_bot.cogs.utils.responsetracker",
    "potato_bot.cogs.accents",
    "potato_bot.cogs.chat",
    "potato_bot.cogs.fun",
    "potato_bot.cogs.images",
    "potato_bot.cogs.meta",
    "potato_bot.cogs.techadmin",
    "potato_bot.cogs.unitystation",
)


class GuildSettings:
    __slots__ = (
        "prefix",
        "prefix_re",
    )

    def __init__(self, bot: Bot, data: edgedb.Object):
        self.prefix = data.prefix

        # custom prefix or mention
        # this way prefix logic is simplified and it hopefully runs faster at a cost of
        # storing duplicate mention regexes
        self.prefix_re = re.compile(
            fr"(?:{re.escape(data.prefix)}|<@!?{bot.user.id}>)\s*"
        )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} prefix={self.prefix}>"


class UserGuildSettings:
    __slots__ = ("accents",)

    def __init__(self, bot: Bot, data: edgedb.Object):
        self.accents = data.accents

    def __repr__(self) -> str:
        return f"<{type(self).__name__} accents={self.accents}>"


class Bot(commands.Bot):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            command_prefix=PREFIX,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(
                roles=False, everyone=False, users=True
            ),
            intents=discord.Intents(
                guilds=True,
                members=True,
                bans=True,
                emojis=True,
                messages=True,
                reactions=True,
            ),
            **kwargs,
        )

        self.session = aiohttp.ClientSession(headers={"user-agent": "PotatoBot"})

        self.guild_settings: Dict[int, GuildSettings] = {}

        self.mention_prefix_re: Optional[re.Pattern[str]] = None

        self.owner_ids: Set[int] = set()

        self.loop.run_until_complete(self.critical_setup())
        self.loop.create_task(self.setup())

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                log.error(f"Error loading {extension}: {type(e).__name__} - {e}")
                traceback.print_exc()

    async def get_prefix(self, message: discord.Message) -> Union[List[str], str]:
        if self.mention_prefix_re is None:
            # prefixes are not initialized
            return []

        prefix_re = self.mention_prefix_re

        if message.guild:
            if (settings := self.guild_settings.get(message.guild.id)) :
                prefix_re = settings.prefix_re

        if (match := prefix_re.match(message.content)) :
            return match[0]

        if message.guild:
            return []

        # allow empty match in DMs
        return ""

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user}!")
        print(f"Prefix: {PREFIX}")

    async def critical_setup(self) -> None:
        self.edb = await edgedb.create_async_pool(
            dsn=os.environ["EDGEDB_DSN"], min_size=1, max_size=2
        )

    async def _get_guild_settings(self) -> None:
        for guild_settings in await self.edb.query(
            """
            SELECT GuildSettings {
                guild_id,
                prefix,
            }
            """
        ):
            self.guild_settings[guild_settings.guild_id] = GuildSettings(
                self, guild_settings
            )

    async def _fetch_owners(self) -> None:
        app_info = await self.application_info()
        if app_info.team is None:
            self.owner_ids = set((app_info.owner.id,))
        else:
            self.owner_ids = set(m.id for m in app_info.team.members)

    async def setup(self) -> None:
        await self.wait_until_ready()

        self.mention_prefix_re = re.compile(
            fr"<@!?{self.user.id}>|{re.escape(PREFIX)}\s*"
        )

        await self._get_guild_settings()

        await self._fetch_owners()

    async def close(self) -> None:
        await self.edb.aclose()
        await self.session.close()

        await super().close()

    async def get_context(
        self, message: discord.Message, *, cls: Type[discord.ext.Context] = None
    ) -> Context:
        return await super().get_context(message, cls=cls or Context)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        sentry_sdk.set_user({"id": message.author.id, "username": str(message.author)})
        sentry_sdk.set_context("channel", {"id": message.channel.id})
        sentry_sdk.set_context(
            "guild", {"id": None if message.guild is None else message.guild.id}
        )

        await self.process_commands(message)

    async def on_command_error(self, ctx: Context, e: BaseException) -> None:
        pass
