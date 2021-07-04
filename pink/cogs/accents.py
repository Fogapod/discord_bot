from __future__ import annotations

import re
import json
import random
import logging
import importlib
import contextlib

from typing import Any, Dict, List, Iterable, Optional
from pathlib import Path

import discord

from discord.ext import commands
from pink_accents import Accent, load_from

from pink.bot import Bot
from pink.cog import Cog
from pink.utils import LRU
from pink.context import Context

ACCENT_WEBHOOK_NAME = "PINK bot accent webhook"

REQUIRED_PERMS = discord.Permissions(
    send_messages=True, manage_messages=True, manage_webhooks=True
)

load_from(Path("accents"))

# probably related:
# https://github.com/python/typing/issues/760
# for some reason mypy does not understand that str can be compared
ALL_ACCENTS = {
    a.name.lower(): a for a in sorted(Accent.get_all_accents(), key=lambda a: a.name)  # type: ignore
}

log = logging.getLogger(__name__)


# inherit to make linters sleep well
class PINKAccent(Accent, register=False):
    MIN_SEVERITY = 1
    MAX_SEVERITY = 10

    @classmethod
    async def convert(cls, ctx: Context, argument: str) -> Accent:
        match = re.match(r"(.+?)(:?\[(\d+)\])?$", argument)
        assert match

        name = match[1]
        severity = 1 if match[3] is None else int(match[3])

        prepared = name.replace(" ", "_").lower()
        try:
            accent = ALL_ACCENTS[prepared]
        except KeyError:
            raise commands.BadArgument(f'Accent "{name}" does not exist')

        if not (cls.MIN_SEVERITY <= severity <= cls.MAX_SEVERITY):
            raise commands.BadArgument(
                f"{accent}: severity must be between {cls.MIN_SEVERITY} and {cls.MAX_SEVERITY}"
            )

        return accent(severity)


_UserAccentsType = Iterable[Accent]


class Accents(Cog):
    """Commands for managing accents."""

    # this is extremely stupid, but required for hooks
    instance: Accents

    MAX_ACCENTS_PER_USER = 10

    def __init__(self, bot: Bot):
        Accents.instance = self

        super().__init__(bot)

        # channel_id -> Webhook
        self._webhooks = LRU(50)

        # guild_id -> user_id -> [Accent]
        self._accents: Dict[int, Dict[int, List[Accent]]] = {}

    async def setup(self) -> None:
        for settings in await self.bot.edb.query(
            """
            SELECT AccentSettings {
                guild_id,
                user_id,
                accents,
            }
            """
        ):
            accents = []
            for accent in settings.accents:
                if (accent_cls := ALL_ACCENTS.get(accent.name.lower())) is None:
                    log.error(
                        f"unknown accent: "
                        f"guild={settings.guild_id} user={settings.user_id} {accent}"
                    )

                    continue

                accents.append(accent_cls(accent.severity))

            if settings.guild_id not in self._accents:
                self._accents[settings.guild_id] = {}

            self._accents[settings.guild_id][settings.user_id] = accents

    def get_user_accents(self, member: discord.Member) -> _UserAccentsType:
        if member.guild.id not in self._accents:
            self._accents[member.guild.id] = {}

        return self._accents[member.guild.id].get(member.id, [])

    def set_user_accents(
        self, member: discord.Member, accents: _UserAccentsType
    ) -> None:
        if member.guild.id not in self._accents:
            self._accents[member.guild.id] = {}

        self._accents[member.guild.id][member.id] = list(accents)

    @commands.group(invoke_without_command=True, ignore_extra=False)
    async def accent(self, ctx: Context) -> None:
        """
        Accent management.

        In order to set accent severity use square brackets: OwO[10]
        """

        await ctx.send_help(ctx.command)

    @commands.command()
    async def accents(self, ctx: Context, user: discord.Member = None) -> None:
        """Alias for accent list"""

        await ctx.invoke(self.list, user=user)

    @accent.command()
    @commands.guild_only()
    async def list(self, ctx: Context, user: discord.Member = None) -> None:
        """List accents for user"""

        if user is None:
            user = ctx.author
        else:
            if user.bot and user.id != ctx.me.id:
                return await ctx.send("Bots cannot have accents")

        user_accent_map = {a.name: a for a in self.get_user_accents(user)}

        body = ""

        longest_name = max(len(k) for k in ALL_ACCENTS.keys())

        for accent in sorted(
            Accent.get_all_accents(),
            key=lambda a: (a.name not in user_accent_map, a.name),
        ):
            # mypy is unable to understand class properties
            if instance := user_accent_map.get(accent.name):  # type: ignore
                line = (
                    f"+ {instance.full_name:>{longest_name}} : {accent.description}\n"
                )
            else:
                line = f"- {accent.name:>{longest_name}} : {accent.description}\n"

            body += line

        await ctx.send(
            f"**{user}** accents (applied from top to bottom): ```diff\n{body}```",
            # override applied accents because getting accent list is a very serious
            # task that should not be obscured
            accents=[],
        )

    async def _add_accents(
        self, ctx: Context, member: discord.Member, accents: _UserAccentsType
    ) -> None:
        user_accent_map = {a.name: a for a in self.get_user_accents(member)}

        something_changed = False

        for accent_to_add in set(accents):
            existing = user_accent_map.get(accent_to_add.name)

            if existing is None or existing.severity != accent_to_add.severity:
                user_accent_map[accent_to_add.name] = accent_to_add

                something_changed = True

        if not something_changed:
            await ctx.send("Nothing to do", exit=True)

        if len(user_accent_map) > self.MAX_ACCENTS_PER_USER:
            await ctx.send(
                f"Cannot have more than **{self.MAX_ACCENTS_PER_USER}** enabled at once",
                exit=True,
            )

        all_accents = list(user_accent_map.values())

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
            updated = []
        else:
            user_accent_map = {a.name: a for a in self.get_user_accents(member)}

            something_changed = False

            for accent_to_remove in set(accents):
                if accent_to_remove.name in user_accent_map:
                    del user_accent_map[accent_to_remove.name]

                    something_changed = True

            if not something_changed:
                await ctx.send("Nothing to do", exit=True)

            updated = list(user_accent_map.values())

        self.set_user_accents(member, updated)

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
            accents=json.dumps([(a.name, a.severity) for a in updated]),
        )

    async def _update_nick(self, ctx: Context) -> None:
        new_nick = ctx.me.name
        for accent in self.get_user_accents(ctx.me):
            new_nick = accent.apply(new_nick, limit=32).strip()

        with contextlib.suppress(discord.Forbidden):
            await ctx.me.edit(nick=new_nick)

    @accent.group(name="bot", invoke_without_command=True, ignore_extra=False)
    @commands.has_permissions(manage_guild=True)
    async def _bot_accent(self, ctx: Context) -> None:
        """Manage bot accents"""

        await ctx.send_help(ctx.command)

    @_bot_accent.command(name="add", aliases=["enable", "on"])
    @commands.has_permissions(manage_guild=True)
    async def add_bot_accent(self, ctx: Context, *accents: PINKAccent) -> None:
        """Add bot accents"""

        if not accents:
            return await ctx.send("No accents provided")

        await self._add_accents(ctx, ctx.me, accents)

        await self._update_nick(ctx)

        await ctx.send("Added bot accents")

    @_bot_accent.command(name="remove", aliases=["disable", "off", "del"])
    @commands.has_permissions(manage_guild=True)
    async def remove_bot_accent(self, ctx: Context, *accents: PINKAccent) -> None:
        """
        Remove bot accents

        Removes all if used without arguments
        """

        await self._remove_accents(ctx, ctx.me, accents)

        await self._update_nick(ctx)

        await ctx.send("Removed bot accents")

    @accent.command(name="add", aliases=["enable", "on"])
    @commands.bot_has_permissions(manage_messages=True, manage_webhooks=True)
    async def add_accent(self, ctx: Context, *accents: PINKAccent) -> None:
        """Add personal accents"""

        if not accents:
            return await ctx.send("No accents provided")

        await self._add_accents(ctx, ctx.author, accents)

        await ctx.send("Added personal accents")

    @accent.command(name="remove", aliases=["disable", "off"])
    @commands.guild_only()
    async def remove_accent(self, ctx: Context, *accents: PINKAccent) -> None:
        """
        Remove personal accents

        Removes all if used without arguments
        """

        await self._remove_accents(ctx, ctx.author, accents)

        await ctx.send("Removed personal accents")

    @accent.command(name="use")
    async def accent_use(self, ctx: Context, accent: PINKAccent, *, text: str) -> None:
        """Apply specified accent to text"""

        await ctx.send(text, accents=[accent])

    @accent.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, manage_webhooks=True)
    async def purge(self, ctx: Context, limit: int = 50) -> None:
        """Remove accent webhook messages in case of spam"""

        lower_limit = 1
        upper_limit = 1000

        if not lower_limit <= limit <= upper_limit:
            return await ctx.send(
                f"Limit should be between **{lower_limit}** and **{upper_limit}**"
            )

        if (
            accent_webhook := await self._get_cached_webhook(ctx.channel, create=False)
        ) is None:
            return await ctx.send(
                "There is no accent webhook in this channel. Nothing to delete"
            )

        message_counts = {}

        def is_accent_webhook(m: discord.Message) -> bool:
            if m.webhook_id != accent_webhook.id:
                return False

            user_name = m.author.name

            message_counts[user_name] = message_counts.get(user_name, 0) + 1

            return True

        async with ctx.typing():
            deleted = await ctx.channel.purge(
                limit=limit, check=is_accent_webhook, before=ctx.message.created_at
            )

            if not deleted:
                return await ctx.send("No accent messages found")

            message_counts_table = "\n".join(
                f"{name}: {count}" for name, count in message_counts.items()
            )

            await ctx.send(
                f"Deleted **{len(deleted)}** out of **{limit}** message(s) from:"
                f"```\n{message_counts_table}```"
            )

    @commands.command()
    @commands.guild_only()
    async def owo(self, ctx: Context) -> None:
        """OwO what's this"""

        owo = ALL_ACCENTS["owo"]
        my_accents = [a.name for a in self.get_user_accents(ctx.me)]

        if owo.name in my_accents:
            await self._remove_accents(ctx, ctx.me, [owo(1)])
        else:
            await self._add_accents(ctx, ctx.me, [owo(severity=random.randint(1, 3))])

        await self._update_nick(ctx)

        await ctx.send("owo toggled")

    @commands.command(aliases=["clown"])
    @commands.guild_only()
    async def honk(self, ctx: Context) -> None:
        """LOUD == FUNNY HONK!"""

        honk = ALL_ACCENTS["clown"]
        my_accents = [a.name for a in self.get_user_accents(ctx.me)]

        if honk.name in my_accents:
            await self._remove_accents(ctx, ctx.me, [honk(1)])
        else:
            await self._add_accents(ctx, ctx.me, [honk(severity=random.choice((1, 2)))])

        await self._update_nick(ctx)

        await ctx.send("honk toggled")

    @staticmethod
    def _apply_accents(content: str, accents: _UserAccentsType) -> str:
        for accent in accents:
            content = accent.apply(content)

        return content.strip()

    def apply_member_accents_to_text(self, *, member: discord.Member, text: str) -> str:
        accents = self.get_user_accents(member)

        return self._apply_accents(text, accents)

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

        # TODO: some other way to prevent accent trigger that is not a missing feature?

        if not (accents := self.get_user_accents(message.author)):
            return

        if not message.channel.permissions_for(message.guild.me).is_superset(
            REQUIRED_PERMS
        ):
            # NOTE: the decision has been made for this to fail silently.
            # this adds some overhead, but makes bot setup much simplier.
            #
            # TODO: find the other way to tell this to users so that they don't think
            # bot is broken. maybe help text?
            return

        if (ctx := await self.bot.get_context(message)).valid:
            return

        if (
            content := self._apply_accents(message.content, accents)
        ) == message.content:
            return

        try:
            await self._send_new_message(ctx, content, message)
        except (discord.NotFound, discord.InvalidArgument):
            # InvalidArgument appears in some rare cases when webhooks is deleted or is
            # owned by other bot
            #
            # cached webhook is missing, should invalidate cache
            del self._webhooks[message.channel.id]

            try:
                await self._send_new_message(ctx, content, message)
            except Exception as e:
                await ctx.reply(
                    f"Accents error: unable to deliver message after invalidating cache: **{e}**.\n"
                    f"Try deleting webhook **{ACCENT_WEBHOOK_NAME}** manually."
                )

                # NOTE: is it really needed? what else could trigger this?
                # return
                raise

        await message.delete()

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
    bot.add_cog(Accents(bot))
