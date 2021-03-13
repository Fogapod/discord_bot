from __future__ import annotations

import re
import json
import random
import importlib

from typing import Any, Dict, List, Union, Optional, Sequence
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
        assert match

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

    def apply(self, text: str, **kwargs: Any) -> str:
        return self.accent.apply(text, severity=self.severity, **kwargs)

    @property
    def name(self) -> str:
        return str(self.accent)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Accent):
            return self.accent == other

        if not isinstance(other, type(self)):
            raise NotImplementedError

        return self.accent == other.accent

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        name = self.name

        if self.severity != 1:
            name += f"[{self.severity}]"

        return name

    def __repr__(self) -> str:
        return f"<{type(self).__name__} accent={self.accent} severity={self.severity}>"


_UserAccentsType = Sequence[AccentWithSeverity]


class Accents(Cog):
    """Commands for managing accents."""

    # required for hooks
    instance: Accents

    MAX_ACCENTS_PER_USER = 10

    def __init__(self, bot: Bot):
        Accents.instance = self

        super().__init__(bot)

        # channel_id -> Webhook
        self._webhooks = LRU(50)

        self._accents: Dict[int, Dict[int, List[AccentWithSeverity]]] = {}

    async def setup(self) -> None:
        for accent in await self.bot.edb.query(
            """
            SELECT AccentSettings {
                guild_id,
                user_id,
                accents,
            }
            """
        ):
            if accent.guild_id not in self._accents:
                self._accents[accent.guild_id] = {}

            self._accents[accent.guild_id][accent.user_id] = [
                AccentWithSeverity(Accent.get_by_name(a.name), severity=a.severity)
                for a in accent.accents
            ]

    def get_user_accents(self, member: discord.Member) -> _UserAccentsType:
        if member.guild.id not in self._accents:
            self._accents[member.guild.id] = {}

        return self._accents[member.guild.id].get(member.id, [])

    def set_user_accents(self, member: discord.Member, accents: Any) -> None:
        if member.guild.id not in self._accents:
            self._accents[member.guild.id] = {}

        self._accents[member.guild.id][member.id] = accents

    @commands.group(
        invoke_without_command=True, ignore_extra=False, aliases=["accents"]
    )
    async def accent(self, ctx: Context) -> None:
        """
        Accent management.

        In order to set accent severity use square brackets: OwO[10]
        """

        await ctx.send_help(ctx.command)

    @accent.command()
    @commands.guild_only()
    async def list(self, ctx: Context, user: discord.Member = None) -> None:
        """List accents for user"""

        if user is None:
            user = ctx.author
        else:
            if user.bot and user.id != ctx.me.id:
                return await ctx.send("Bots cannot have accents")

        accents = self.get_user_accents(user)

        # I have no idea why this is not in stdlib, string has find method
        def sequence_find(seq: Sequence[Any], item: Any, default: int = -1) -> int:
            for i, j in enumerate(seq):
                if j == item:
                    return i

            return default

        # accent objects are used for comparison
        accent_map = {a.accent: a for a in accents}

        all_accents = Accent.all_accents()

        body = ""

        for accent in sorted(
            all_accents,
            key=lambda a: (
                # sort by position in global accent list, leave missing at the end
                sequence_find(accents, a, len(all_accents)),
                # sort the rest by names
                str(a).lower(),
            ),
        ):
            if accent in accent_map:
                line = f"+ {accent_map[accent]}\n"
            else:
                line = f"- {accent}\n"

            body += line

        await ctx.send(
            f"**{user}** accents (applied from top to bottom): ```diff\n{body}```"
        )

    async def _add_accents(
        self, ctx: Context, member: discord.Member, accents: _UserAccentsType
    ) -> None:
        # deduplicate using names
        accents = list(dict.fromkeys(accents))

        all_accents = {a: a for a in self.get_user_accents(member)}

        something_updated = False

        for accent_to_add in accents:
            existing = all_accents.get(accent_to_add)
            if existing is None or existing.severity != accent_to_add.severity:
                something_updated = True
                all_accents[accent_to_add] = accent_to_add

        if not something_updated:
            await ctx.send("Nothing to do", exit=True)

        if len(all_accents) > self.MAX_ACCENTS_PER_USER:
            await ctx.send(
                f"Cannot have more than **{self.MAX_ACCENTS_PER_USER}** enabled at once",
                exit=True,
            )

        all_accents = list(all_accents)  # type: ignore

        self.set_user_accents(member, all_accents)

        # json cast because tuples are not supported
        # https://github.com/edgedb/edgedb/issues/2334#issuecomment-793041555
        await ctx.bot.edb.query(
            """
            INSERT AccentSettings {
                guild_id := <snowflake>$guild_id,
                user_id  := <snowflake>$user_id,
                accents  := <array<tuple<str, int16>>><json>$accents,
            } UNLESS CONFLICT ON .exclusive_hack
            ELSE (
                UPDATE AccentSettings
                SET {
                    accents := <array<tuple<str, int16>>><json>$accents,
                }
            )
            """,
            guild_id=ctx.guild.id,
            user_id=member.id,
            accents=json.dumps([(a.name, a.severity) for a in all_accents]),
        )

    async def _remove_accents(
        self, ctx: Context, member: discord.Member, accents: _UserAccentsType
    ) -> None:
        if not accents:
            all_accents: Union[
                Dict[AccentWithSeverity, AccentWithSeverity], List[AccentWithSeverity]
            ] = []
        else:
            # deduplicate using names
            accents = list(dict.fromkeys(accents))

            all_accents = {a: a for a in self.get_user_accents(member)}

            something_updated = False

            for accent_to_remove in accents:
                if accent_to_remove in all_accents:
                    something_updated = True
                    del all_accents[accent_to_remove]

            if not something_updated:
                await ctx.send("Nothing to do", exit=True)

            all_accents = list(all_accents)

        self.set_user_accents(member, all_accents)

        # json cast because tuples are not supported
        # https://github.com/edgedb/edgedb/issues/2334#issuecomment-793041555
        await self.bot.edb.query(
            """
            UPDATE AccentSettings
            FILTER .guild_id = <snowflake>$guild_id AND .user_id = <snowflake>$user_id
            SET {
                accents := <array<tuple<str, int16>>><json>$accents,
            }
            """,
            guild_id=ctx.guild.id,
            user_id=member.id,
            accents=json.dumps([(a.name, a.severity) for a in all_accents]),
        )

    async def _update_nick(self, ctx: Context) -> None:
        new_nick = ctx.me.name
        for accent in self.get_user_accents(ctx.me):
            new_nick = accent.apply(new_nick, limit=32).strip()

        await ctx.me.edit(nick=new_nick)

    @accent.group(name="bot", invoke_without_command=True, ignore_extra=False)
    @commands.has_permissions(manage_guild=True)
    async def _bot_accent(self, ctx: Context) -> None:
        """Manage bot accents"""

        await ctx.send_help(ctx.command)

    @_bot_accent.command(name="add", aliases=["enable", "on"])
    @commands.has_permissions(manage_guild=True)
    async def add_bot_accent(self, ctx: Context, *accents: AccentWithSeverity) -> None:
        """Add bot accents"""

        if not accents:
            return await ctx.send("No accents provided")

        await self._add_accents(ctx, ctx.me, accents)

        await self._update_nick(ctx)

        await ctx.send("Added bot accents")

    @_bot_accent.command(name="remove", aliases=["disable", "off"])
    @commands.has_permissions(manage_guild=True)
    async def remove_bot_accent(
        self, ctx: Context, *accents: AccentWithSeverity
    ) -> None:
        """
        Remove bot accents

        Removes all if used without arguments
        """

        await self._remove_accents(ctx, ctx.me, accents)

        await self._update_nick(ctx)

        await ctx.send("Removed bot accents")

    @accent.command(name="add", aliases=["enable", "on"])
    @commands.bot_has_permissions(manage_messages=True, manage_webhooks=True)
    async def add_accent(self, ctx: Context, *accents: AccentWithSeverity) -> None:
        """Add personal accents"""

        if not accents:
            return await ctx.send("No accents provided")

        await self._add_accents(ctx, ctx.author, accents)

        await ctx.send("Added personal accents")

    @accent.command(name="remove", aliases=["disable", "off"])
    @commands.guild_only()
    async def remove_accent(self, ctx: Context, *accents: AccentWithSeverity) -> None:
        """
        Remove personal accents

        Removes all if used without arguments
        """

        await self._remove_accents(ctx, ctx.author, accents)

        await ctx.send("Removed personal accents")

    @accent.command(name="use")
    async def accent_use(
        self, ctx: Context, accent: AccentWithSeverity, *, text: str
    ) -> None:
        """Apply specified accent to text"""

        await ctx.send(text, accents=[accent])

    @accent.command(aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, manage_webhooks=True)
    async def clean(self, ctx: Context, limit: int = 100) -> None:
        """Removes webhook messages from channel, checking up to `limit` messages"""

        upper_limit = 1000
        if limit > upper_limit:
            return await ctx.send(f"Limit should be between 1 and {upper_limit}")

        if (
            accent_webhook := await self._get_cached_webhook(ctx.channel, create=False)
        ) is None:
            return await ctx.send(
                "There is no accent webhook in this channel. Nothing to delete"
            )

        def is_accent_webhook(m: discord.Message) -> bool:
            return m.webhook_id == accent_webhook.id  # type: ignore

        async with ctx.typing():
            deleted = await ctx.channel.purge(limit=limit, check=is_accent_webhook)
            await ctx.send(f"Deleted **{len(deleted)}** out of **{limit}** message(s)")

    @commands.command()
    @commands.guild_only()
    async def owo(self, ctx: Context) -> None:
        """OwO what's this"""

        owo = Accent.get_by_name("OwO")
        my_accents = self.get_user_accents(ctx.me)

        if owo in my_accents:
            await self._remove_accents(ctx, ctx.me, [AccentWithSeverity(owo)])
        else:
            await self._add_accents(
                ctx, ctx.me, [AccentWithSeverity(owo, severity=random.randint(1, 3))]
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
        accents: Optional[_UserAccentsType] = None,
        **kwargs: Any,
    ) -> discord.Message:
        if content is not None:
            if accents is None:
                if ctx.guild is not None:
                    accents = Accents.instance.get_user_accents(ctx.me)
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
        accents: Optional[_UserAccentsType] = None,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if content is not None:
            if accents is None:
                if ctx.guild is not None:
                    accents = Accents.instance.get_user_accents(ctx.me)
                else:
                    accents = []

            content = Accents._apply_accents(str(content), accents)

        return await original(ctx, message, content=content, **kwargs)

    async def _replace_message(self, message: discord.Message) -> None:
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

        if not (accents := self.get_user_accents(message.author)):
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
        self,
        channel: discord.TextChannel,
        create: bool = True,
    ) -> Optional[discord.Webhook]:
        if (wh := self._webhooks.get(channel.id)) is None:
            for wh in await channel.webhooks():
                if wh.name == ACCENT_WEBHOOK_NAME:
                    break
            else:
                if not create:
                    return None

                wh = await channel.create_webhook(name=ACCENT_WEBHOOK_NAME)

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
    async def on_message(self, message: discord.Message) -> None:
        await self._replace_message(message)

    # needed in case people use command and edit their message
    @Cog.listener()
    async def on_message_edit(self, old: discord.Message, new: discord.Message) -> None:
        await self._replace_message(new)


def load_accents() -> None:
    for child in (Path(__file__).parent / "accents").iterdir():
        if child.suffix != ".py":
            continue

        if child.name.startswith("__"):
            continue

        if child.name == "accent.py":
            continue

        importlib.import_module(f"{__name__}.accents.{child.stem}")


def setup(bot: Bot) -> None:
    load_accents()

    bot.add_cog(Accents(bot))
