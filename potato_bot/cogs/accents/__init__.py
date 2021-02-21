from __future__ import annotations

import re
import random
import importlib

from typing import Any, Dict, Union, Optional, Sequence
from pathlib import Path

import discord

from discord.ext import commands

from potato_bot.bot import Bot
from potato_bot.cog import Cog
from potato_bot.utils import LRU
from potato_bot.context import Context

from .accents.accent import Accent

ACCENT_WEBHOOK_NAME = "PotatoBot accent Webhook"

REQUIRED_PERMS = discord.Permissions(
    send_messages=True, manage_messages=True, manage_webhooks=True
)


class AccentWithSeverity:
    __slots__ = (
        "accent",
        "severity",
    )

    MIN_SEVERITY = 1
    MAX_SEVERITY = 10

    @classmethod
    async def convert(cls, ctx: Context, argument: str) -> AccentWithSeverity:
        match = re.match(r"(.+?)(:?\[(\d+)\])?$", argument)
        name = match[1]
        severity = 1 if match[3] is None else int(match[3])

        prepared = name.replace(" ", "_")
        try:
            accent = Accent.get_by_name(prepared)
        except KeyError:
            raise commands.BadArgument(f'Accent "{name}" does not exist')

        if not (cls.MIN_SEVERITY <= severity <= cls.MAX_SEVERITY):
            raise commands.BadArgument(
                f"{accent}: severity must be between {cls.MIN_SEVERITY} and {cls.MAX_SEVERITY}"
            )

        return cls(accent, severity=severity)

    def __init__(self, accent: Accent, *, severity: int = 1):
        self.accent = accent
        self.severity = severity

    def apply(self, text: str, **kwargs) -> str:
        return self.accent.apply(text, severity=self.severity, **kwargs)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Accent):
            return self.accent == other

        if not isinstance(other, type(self)):
            raise NotImplementedError

        return self.accent == other.accent

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash(self.accent)

    def __str__(self) -> str:
        name = str(self.accent)

        if self.severity != 1:
            name += f"[{self.severity}]"

        return name

    def __repr__(self):
        return f"<{type(self).__name__} accent={self.accent} severity={self.severity}>"


_UserAccentsType = Sequence[AccentWithSeverity]


class Accents(Cog):
    """Commands for managing accents."""

    # guild_id -> user_id -> accents
    # this has to be class variable because of hooks
    accent_settings: Dict[int, Dict[int, _UserAccentsType]] = {}

    MAX_ACCENTS_PER_USER = 10

    def __init__(self, bot: Bot):
        super().__init__(bot)

        # channel_id -> Webhook
        self._webhooks = LRU(50)

    async def setup(self):
        async with self.bot.db.cursor() as cur:
            await cur.execute("SELECT * FROM user_accent")
            accents = await cur.fetchall()

        for row in accents:
            accent = AccentWithSeverity(
                Accent.get_by_name(row["accent"]), severity=row["severity"]
            )

            guild_id = row["guild_id"]
            user_id = row["user_id"]

            if guild_id not in self.accent_settings:
                self.accent_settings[guild_id] = {}

            if user_id not in self.accent_settings[guild_id]:
                self.accent_settings[guild_id][user_id] = []

            self.accent_settings[guild_id][user_id].append(accent)

    @classmethod
    def get_user_accents(cls, guild_id: int, user_id: int) -> _UserAccentsType:
        if guild_id not in cls.accent_settings:
            cls.accent_settings[guild_id] = {}

        return cls.accent_settings[guild_id].get(user_id, [])

    @commands.group(
        invoke_without_command=True, ignore_extra=False, aliases=["accents"]
    )
    async def accent(self, ctx: Context):
        """
        Accent management.

        In order to set accent severity use square brackets: OwO[100]
        """

        await ctx.send_help(ctx.command)

    def _format_accent_list(self, accents: _UserAccentsType) -> str:
        body = ""

        # I have no idea why this is not in stdlib, string has find method
        def sequence_find(seq: Sequence[Any], item: Any, default: int = -1) -> int:
            for i, j in enumerate(seq):
                if j == item:
                    return i

            return default

        # accent objects are used for comparison
        accent_map = {a.accent: a for a in accents}

        all_accents = Accent.all_accents()

        for accent in sorted(
            all_accents,
            key=lambda a: (
                # sort by position in global accent list, leave missing at the end
                sequence_find(accent_map.keys(), a, len(all_accents)),
                # sort the rest by names
                str(a).lower(),
            ),
        ):
            if accent in accent_map:
                line = f"+ {accent_map[accent]}\n"
            else:
                line = f"- {accent}\n"

            body += line

        return body

    async def _add_accents(self, ctx: Context, user_id: int, accents: _UserAccentsType):
        current_accents = self.get_user_accents(ctx.guild.id, user_id)

        if not (to_add := set(accents).difference(current_accents)):
            await ctx.send("Nothing to add", exit=True)

        if len(current_accents) + len(to_add) > self.MAX_ACCENTS_PER_USER:
            await ctx.send(
                f"Cannot have more than **{self.MAX_ACCENTS_PER_USER}** enabled at once",
                exit=True,
            )

        # sets are nice, but we must preserve order here
        to_add = sorted(to_add, key=lambda x: accents.index(x))

        current_accents.extend(to_add)

        self.accent_settings[ctx.guild.id][user_id] = current_accents

        async with ctx.db.cursor(commit=True) as cur:
            await cur.executemany(
                """
                INSERT OR REPLACE INTO user_accent (
                    guild_id,
                    user_id,
                    accent,
                    severity
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                [
                    (ctx.guild.id, user_id, str(accent.accent), accent.severity)
                    for accent in to_add
                ],
            )

    async def _remove_accents(
        self, ctx: Context, user_id: int, accents: _UserAccentsType
    ):
        current_accents = self.get_user_accents(ctx.guild.id, user_id)

        if not accents:
            accents = current_accents

        if not (to_remove := set(current_accents).intersection(accents)):
            await ctx.send("Nothing to remove", exit=True)

        self.accent_settings[ctx.guild.id][user_id] = [
            a for a in current_accents if a not in to_remove
        ]

        def accent_name(accent: Union[Accent, AccentWithSeverity]) -> str:
            # this is a hack for owo command.
            # since Accent and AccentWithSeverity instances have same hashes,
            # it is possible to use them interchangeably there, but names work
            # differently
            if isinstance(accent, AccentWithSeverity):
                accent = accent.accent

            return str(accent)

        async with ctx.db.cursor(commit=True) as cur:
            await cur.executemany(
                """
                DELETE FROM user_accent
                WHERE
                    guild_id = ? AND
                    user_id = ? AND
                    accent = ?
                """,
                [(ctx.guild.id, user_id, accent_name(accent)) for accent in to_remove],
            )

    async def _update_nick(self, ctx: Context):
        new_nick = ctx.me.name
        for accent in self.get_user_accents(ctx.guild.id, ctx.me.id):
            new_nick = accent.apply(new_nick, limit=32).strip()

        await ctx.me.edit(nick=new_nick)

    @accent.group(name="bot", invoke_without_command=True, ignore_extra=False)
    async def _bot_accent(self, ctx: Context):
        """Manage bot accents, lists accents without arguments"""

        accents = self.get_user_accents(ctx.guild.id, ctx.me.id)
        formatted_list = self._format_accent_list(accents)

        await ctx.send(
            f"Bot accents (applied from top to bottom): ```diff\n{formatted_list}```"
        )

    @_bot_accent.command(name="add", aliases=["enable", "on"])
    @commands.has_permissions(manage_guild=True)
    async def _bot_accent_add(self, ctx: Context, *accents: AccentWithSeverity):
        """Add bot accents"""

        if not accents:
            return await ctx.send("No accents provided")

        await self._add_accents(ctx, ctx.me.id, accents)

        await self._update_nick(ctx)

        await ctx.send("Added bot accents")

    @_bot_accent.command(name="remove", aliases=["disable", "off"])
    @commands.has_permissions(manage_guild=True)
    async def _bot_accent_remove(self, ctx: Context, *accents: AccentWithSeverity):
        """
        Remove bot accents

        Removes all if used without arguments
        """

        await self._remove_accents(ctx, ctx.me.id, accents)

        await self._update_nick(ctx)

        await ctx.send("Removed bot accents")

    @accent.command(name="use")
    async def accent_use(self, ctx: Context, accent: AccentWithSeverity, *, text: str):
        """Apply specified accent to text"""

        await ctx.send(text, accents=[accent])

    @accent.group(
        name="me",
        invoke_without_command=True,
        ignore_extra=False,
    )
    @commands.guild_only()
    async def my_accents(self, ctx: Context):
        """Manage your accents, lists accents without arguments"""

        accents = self.get_user_accents(ctx.guild.id, ctx.author.id)
        formatted_list = self._format_accent_list(accents)

        await ctx.send(
            f"Your accents (applied from top to bottom): ```diff\n{formatted_list}```"
        )

    @my_accents.command(name="add", aliases=["enable", "on"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, manage_webhooks=True)
    async def add_my_accent(self, ctx, *accents: AccentWithSeverity):
        """Add personal accents"""

        if not accents:
            return await ctx.send("No accents provided")

        await self._add_accents(ctx, ctx.author.id, accents)

        await ctx.send("Added personal accents")

    @my_accents.command(name="remove", aliases=["disable", "off"])
    @commands.guild_only()
    async def remove_my_accent(self, ctx, *accents: AccentWithSeverity):
        """
        Remove personal accents

        Removes all if used without arguments
        """

        await self._remove_accents(ctx, ctx.author.id, accents)

        await ctx.send("Removed personal accents")

    @commands.command()
    @commands.guild_only()
    async def owo(self, ctx: Context):
        """OwO what's this"""

        owo = Accent.get_by_name("OwO")
        my_accents = self.get_user_accents(ctx.guild.id, ctx.me.id)

        if owo in my_accents:
            await self._remove_accents(ctx, ctx.me.id, [owo])
        else:
            await self._add_accents(
                ctx, ctx.me.id, [AccentWithSeverity(owo, severity=random.randint(1, 3))]
            )

        await self._update_nick(ctx)

        await ctx.send("owo toggled")

    @staticmethod
    def _apply_accents(content: str, accents: _UserAccentsType) -> str:
        for accent in accents:
            content = accent.apply(content)

        return content

    @Context.hook()
    async def on_send(
        original,
        ctx: Context,
        content: Any = None,
        *,
        accents: Optional[AccentWithSeverity] = None,
        **kwargs: Any,
    ) -> discord.Message:
        if content is not None:
            if accents is None:
                if ctx.guild is not None:
                    accents = Accents.get_user_accents(ctx.guild.id, ctx.me.id)
                else:
                    accents = []

            content = Accents._apply_accents(str(content), accents)

        return await original(ctx, content, **kwargs)

    @Context.hook()
    async def on_edit(
        original,
        ctx: Context,
        message: discord.Message,
        *,
        accents: Optional[AccentWithSeverity] = None,
        content: Optional[str] = None,
        **kwargs: Any,
    ):
        if content is not None:
            if accents is None:
                if ctx.guild is not None:
                    accents = Accents.get_user_accents(ctx.guild.id, ctx.me.id)
                else:
                    accents = []

            content = Accents._apply_accents(str(content), accents)

        return await original(ctx, message, content=content, **kwargs)

    async def _replace_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        if not message.content:
            return

        # there is no easy and reliable way to preserve attachments
        if message.attachments:
            return

        # webhooks do not support references
        if message.reference is not None:
            return

        if not (accents := self.get_user_accents(message.guild.id, message.author.id)):
            return

        if not message.channel.permissions_for(message.guild.me).is_superset(
            REQUIRED_PERMS
        ):
            return

        if (ctx := await self.bot.get_context(message)).valid:
            return

        if (
            content := self._apply_accents(message.content, accents)
        ) == message.content:
            return

        await message.delete()
        try:
            await self._send_new_message(ctx, content, message)
        except discord.NotFound:
            # cached webhook is missing, should invalidate cache
            del self._webhooks[message.channel.id]

            await self._send_new_message(ctx, content, message)

    async def _get_cached_webhook(
        self, channel: discord.TextChannel
    ) -> discord.Webhook:
        if (wh := self._webhooks.get(channel.id)) is None:
            wh_name = ACCENT_WEBHOOK_NAME
            for wh in await channel.webhooks():
                if wh.name == wh_name:
                    break
            else:
                wh = await channel.create_webhook(name=wh_name)

            self._webhooks[channel.id] = wh

        return wh

    async def _send_new_message(
        self,
        ctx: Context,
        content: str,
        original: discord.Message,
    ) -> None:
        await ctx.send(
            content,
            allowed_mentions=discord.AllowedMentions(
                everyone=original.author.guild_permissions.mention_everyone,
                users=True,
                roles=True,
            ),
            target=await self._get_cached_webhook(original.channel),
            register=False,
            accents=[],
            # webhook data
            username=original.author.display_name,
            avatar_url=original.author.avatar_url,
            embeds=original.embeds,
        )

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        await self._replace_message(message)

    # needed in case people use command and edit their message
    @Cog.listener()
    async def on_message_edit(self, old: discord.Message, new: discord.Message):
        await self._replace_message(new)


def load_accents():
    for child in (Path(__file__).parent / "accents").iterdir():
        if child.suffix != ".py":
            continue

        if child.name.startswith("__"):
            continue

        if child.name == "accent.py":
            continue

        importlib.import_module(f"{__name__}.accents.{child.stem}")


def setup(bot: Bot):
    load_accents()

    bot.add_cog(Accents(bot))
