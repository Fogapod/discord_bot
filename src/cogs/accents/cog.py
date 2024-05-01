from __future__ import annotations

import asyncio
import collections
import contextlib
import logging
import random

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import discord

from discord.ext import commands
from pink_accents import Accent

from src.bot import PINK
from src.cache import LRU
from src.cog import Cog
from src.context import Context
from src.converters import Code
from src.errors import PINKError
from src.hooks import HookHost

from .constants import ALL_ACCENTS
from .types import PINKAccent

REQUIRED_PERMS = discord.Permissions(send_messages=True, manage_messages=True, manage_webhooks=True)


log = logging.getLogger(__name__)


_UserAccentsType = Iterable[Accent]


class Accents(Cog, HookHost):
    """Commands for managing accents."""

    MAX_ACCENTS_PER_USER = 10

    def __init__(self, bot: PINK):
        super().__init__(bot)

        # channel_id -> Webhook
        self._webhooks = LRU(64)

        # guild_id -> user_id -> [Accent]
        self._accents: dict[int, dict[int, list[Accent]]] = {}

        # message_id -> webhook_message
        # used for fighting back against discord embed message edits:
        # user sends text message -> discord queues embed creation in background -> edits message on success
        # this triggers accents twice. cached message ids are used to edit original response
        self._sent_webhook_messages = LRU(64)

    async def cog_load(self) -> None:
        # TODO: perform cleanup in case name format or bot name ever changes?
        # current name: PINK
        self.accent_wh_name = f"{self.bot.user.name} bot accent webhook"  # type: ignore

        db = self.bot.db_cursor()
        db.execute("SELECT guild_id, user_id, name, severity FROM accents")
        for settings in db.fetchall():
            if (accent_cls := ALL_ACCENTS.get(settings["name"].lower())) is None:
                log.error(
                    "unknown accent: guild=%s user=%s %s", settings["guild_id"], settings["user_id"], settings["name"]
                )

                continue

            self._accents.setdefault(settings["guild_id"], {})
            self._accents[settings["guild_id"]].setdefault(settings["user_id"], [])

            self._accents[settings["guild_id"]][settings["user_id"]].append(accent_cls(settings["severity"]))

    async def cog_unload(self) -> None:
        self.release_hooks()

    def get_user_accents(self, member: discord.Member) -> _UserAccentsType:
        if member.guild.id not in self._accents:
            self._accents[member.guild.id] = {}

        return self._accents[member.guild.id].get(member.id, [])

    def set_user_accents(self, member: discord.Member, accents: _UserAccentsType) -> None:
        if member.guild.id not in self._accents:
            self._accents[member.guild.id] = {}

        self._accents[member.guild.id][member.id] = list(accents)

    @commands.group(invoke_without_command=True, ignore_extra=False)
    async def accent(self, ctx: Context) -> None:
        """
        Accent management.

        In order to set accent severity use square brackets: OwO[10]

        Some accents might support special severity values, but usually
        severity must be in range [1, 10]
        """

        await ctx.send_help(ctx.command)

    @commands.command(aliases=["ac2l"], hidden=True)
    async def accent2_ls(self, ctx: Context) -> None:
        """list pink_accents: https://github.com/Fogapod/pink_accents"""

        await ctx.reply(", ".join(f.stem for f in sorted(Path("/code/accents2/examples/").iterdir())))

    async def run_accent2(
        self,
        ctx: Context,
        accent: str,
        text: str,
        accent_is_custom: bool,
        intensity: int = 0,
    ) -> None:
        args = [
            "--intensity",
            str(intensity),
        ]

        if accent_is_custom:
            args.extend(("--accent-string", accent))
        else:
            args.extend(
                (
                    "--accent",
                    # this is safe from injections because of .ron at the end (unless at some point ron files are added)
                    f"/code/accents2/examples/{accent}.ron",
                )
            )

        process = await asyncio.create_subprocess_exec(
            "/usr/bin/sayit",
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        assert process.stdin is not None
        process.stdin.write(text.encode())
        process.stdin.write_eof()

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            await ctx.reply(stdout.decode())
        else:
            await ctx.reply(f"```\n{stderr.decode()}```")

    @commands.command(aliases=["ac2"], hidden=True)
    async def accent2(self, ctx: Context, accent: str, intensity: int, *, text: str) -> None:
        """test pink_accents: https://github.com/Fogapod/pink_accents"""

        await self.run_accent2(ctx, accent, text, accent_is_custom=False, intensity=intensity)

    @commands.command(aliases=["ac2c"], hidden=True)
    async def accent2_custom(self, ctx: Context, intensity: int, *, code: Code) -> None:
        """custom pink_accent: https://github.com/Fogapod/pink_accents"""

        await self.run_accent2(ctx, code.body, code.the_rest, accent_is_custom=True, intensity=intensity)

    @commands.command()
    async def accents(self, ctx: Context, user: Optional[discord.Member] = None) -> None:
        """Alias for accent list"""

        await ctx.invoke(self._list, user=user)

    @accent.command(name="list", aliases=["ls"])  # type: ignore
    async def _list(self, ctx: Context, user: Optional[discord.Member] = None) -> None:
        """List accents for user"""

        # we are in DMs
        if ctx.message.guild is None:
            # discord.Member converter looks up global cache in DMs, what a great idea
            user = ctx.author  # type: ignore

            user_accent_map = {}
        else:
            if user is None:
                user = ctx.author  # type: ignore
            else:
                if user.bot and user.id != ctx.me.id:
                    return await ctx.send("Bots cannot have accents")

            user_accent_map = {a.name(): a for a in self.get_user_accents(user)}  # type: ignore[arg-type]

        body = ""

        # I have no idea why this is not in stdlib, string has find method
        def iterable_find(seq: Iterable[Any], item: Any, default: int = -1) -> int:
            for i, j in enumerate(seq):
                if j == item:
                    return i

            return default

        longest_name = max(len(k) for k in ALL_ACCENTS)

        for accent in sorted(
            ALL_ACCENTS.values(),
            key=lambda a: (
                # sort by position in global accent list, leave missing at the end
                -iterable_find(user_accent_map.keys(), a.name()),
                a.name(),
            ),
        ):
            if instance := user_accent_map.get(accent.name()):
                line = f"+ {instance.full_name:>{longest_name}} : {accent.description()}\n"
            else:
                line = f"- {accent.name():>{longest_name}} : {accent.description()}\n"

            body += line

        await ctx.send(
            f"**{user}** accents (applied from bottom to top): ```diff\n{body}```",
            # override applied accents because getting accent list is a very serious
            # task that should not be obscured
            accents=[],
        )

    async def _add_accents(self, ctx: Context, member: discord.Member, accents: _UserAccentsType) -> None:
        user_accent_map = {a.name(): a for a in self.get_user_accents(member)}

        something_changed = False

        # remove duplicates preserving order
        accents = list(dict.fromkeys(accents))

        for accent_to_add in accents:
            existing = user_accent_map.get(accent_to_add.name())

            if existing is None or existing.severity != accent_to_add.severity:
                user_accent_map[accent_to_add.name()] = accent_to_add

                something_changed = True

        if not something_changed:
            raise PINKError("Nothing to do")

        if len(user_accent_map) > self.MAX_ACCENTS_PER_USER:
            raise PINKError(f"Cannot have more than **{self.MAX_ACCENTS_PER_USER}** enabled at once")

        all_accents = list(user_accent_map.values())

        self.set_user_accents(member, all_accents)

        rows = (
            (
                ctx.guild.id,  # type: ignore
                member.id,
                accent.name(),
                accent.severity,
            )
            for accent in all_accents
        )

        ctx.db.executemany(
            "INSERT INTO accents (guild_id, user_id, name, severity) VALUES (?, ?, ?, ?) "
            "ON CONFLICT (guild_id, user_id, name) DO UPDATE "
            "SET name = EXCLUDED.name",
            rows,
        )

    async def _remove_accents(self, ctx: Context, member: discord.Member, accents: _UserAccentsType) -> None:
        # a special case. empty iterable means remove everything
        if not accents:
            await ctx.db.execute(
                "DELETE FROM accents WHERE guild_id = ? AND user_id = ?",
                (
                    ctx.guild.id,  # type: ignore
                    member.id,
                ),
            )

            self.set_user_accents(member, [])

            return

        name_to_accent = {a.name(): a for a in self.get_user_accents(member)}

        to_remove = []

        for accent_to_remove in set(accents):
            if accent_to_remove.name() in name_to_accent:
                to_remove.append(accent_to_remove)

                del name_to_accent[accent_to_remove.name()]

        if not to_remove:
            raise PINKError("Nothing to do")

        self.set_user_accents(member, name_to_accent.values())

        rows = (
            (
                ctx.guild.id,  # type: ignore
                member.id,
                accent.name(),
            )
            for accent in to_remove
        )
        ctx.db.executemany("DELETE FROM accents WHERE guild_id = ? AND user_id = ? AND name = ?", rows)

    async def _update_nick(self, ctx: Context) -> None:
        new_nick = ctx.me.name
        for accent in self.get_user_accents(ctx.me):  # type: ignore
            new_nick = accent.apply(new_nick, limit=32).strip()

        with contextlib.suppress(discord.Forbidden):
            await ctx.me.edit(nick=new_nick)  # type: ignore

    @accent.group(name="bot", invoke_without_command=True, ignore_extra=False)  # type: ignore
    @commands.has_permissions(manage_guild=True)
    async def _bot_accent(self, ctx: Context) -> None:
        """Manage bot accents"""

        await ctx.send_help(ctx.command)

    @_bot_accent.command(name="add", aliases=["enable", "on"])  # type: ignore
    @commands.has_permissions(manage_guild=True)
    async def add_bot_accent(self, ctx: Context, *accents: PINKAccent) -> None:
        """Add bot accents"""

        if not accents:
            raise commands.BadArgument("no accents provided")

        await self._add_accents(ctx, ctx.me, accents)  # type: ignore

        await self._update_nick(ctx)

        await ctx.send("Added bot accents")

    @_bot_accent.command(name="remove", aliases=["disable", "off", "del"])  # type: ignore
    @commands.has_permissions(manage_guild=True)
    async def remove_bot_accent(self, ctx: Context, *accents: PINKAccent) -> None:
        """
        Remove bot accents

        Removes all if used without arguments
        """

        await self._remove_accents(ctx, ctx.me, accents)  # type: ignore

        await self._update_nick(ctx)

        await ctx.send("Removed bot accents")

    @accent.command(name="add", aliases=["enable", "on"])  # type: ignore
    @commands.bot_has_permissions(manage_messages=True, manage_webhooks=True)
    async def add_accent(self, ctx: Context, *accents: PINKAccent) -> None:
        """Add personal accents"""

        if not accents:
            raise commands.BadArgument("no accents provided")

        await self._add_accents(ctx, ctx.author, accents)  # type: ignore

        await ctx.send("Added personal accents")

    @accent.command(name="remove", aliases=["disable", "off"])  # type: ignore
    @commands.guild_only()
    async def remove_accent(self, ctx: Context, *accents: PINKAccent) -> None:
        """
        Remove personal accents

        Removes all if used without arguments
        """

        await self._remove_accents(ctx, ctx.author, accents)  # type: ignore

        await ctx.send("Removed personal accents")

    @accent.command(name="use")  # type: ignore
    async def accent_use(self, ctx: Context, accent: PINKAccent, *, text: str) -> None:
        """Apply specified accent to text"""

        await ctx.send(text, accents=[accent])

    @accent.command()  # type: ignore
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, manage_webhooks=True)
    async def purge(self, ctx: Context, limit: int = 50) -> None:
        """Remove accent webhook messages in case of spam"""

        lower_limit = 1
        upper_limit = 1000

        if not lower_limit <= limit <= upper_limit:
            raise PINKError(f"Limit should be between **{lower_limit}** and **{upper_limit}**")

        if (accent_webhook := await self._get_cached_webhook(ctx.channel, create=False)) is None:  # type: ignore
            raise PINKError("There is no accent webhook in this channel. Nothing to delete")

        message_counts: collections.defaultdict[str, int] = collections.defaultdict(int)

        def is_accent_webhook(m: discord.Message) -> bool:
            if m.webhook_id != accent_webhook.id:
                return False

            message_counts[m.author.name] += 1

            return True

        async with ctx.typing():
            deleted = await ctx.channel.purge(  # type: ignore
                limit=limit,
                check=is_accent_webhook,
                before=ctx.message.created_at,
            )

            if not deleted:
                return await ctx.send("No accent messages found")

            message_counts_table = "\n".join(f"{name}: {count}" for name, count in message_counts.items())

        await ctx.send(
            f"Deleted **{len(deleted)}** out of **{limit}** message(s) from:" f"```\n{message_counts_table}```"
        )

    async def _toggle_bot_accent(
        self,
        ctx: Context,
        accent: type[Accent],
        *,
        min_severity: int = 1,
        max_severity: int = 1,
    ) -> None:
        my_accents = [a.name() for a in self.get_user_accents(ctx.me)]  # type: ignore[arg-type]

        if accent.name() in my_accents:
            await self._remove_accents(ctx, ctx.me, [accent(1)])  # type: ignore[arg-type]
        else:
            if min_severity == max_severity:
                severity = min_severity
            else:
                severity = random.randint(min_severity, max_severity)

            await self._add_accents(ctx, ctx.me, [accent(severity)])  # type: ignore

        await self._update_nick(ctx)

        await ctx.send(f"{accent.name()} toggled")

    @commands.command()
    @commands.guild_only()
    async def owo(self, ctx: Context) -> None:
        """OwO what's this"""

        await self._toggle_bot_accent(ctx, ALL_ACCENTS["owo"], max_severity=3)

    @commands.command(aliases=["clown"])
    @commands.guild_only()
    async def honk(self, ctx: Context) -> None:
        """LOUD == FUNNY HONK!"""

        await self._toggle_bot_accent(ctx, ALL_ACCENTS["clown"])

    @commands.command()
    @commands.guild_only()
    async def kek(self, ctx: Context) -> None:
        """Embrace Da Orks"""

        await self._toggle_bot_accent(ctx, ALL_ACCENTS["ork"])

    @staticmethod
    def apply_accents_to_text(content: str, accents: _UserAccentsType) -> str:
        for accent in accents:
            content = accent.apply(content)

        return content.strip()

    def apply_member_accents_to_text(self, *, member: discord.Member, text: str) -> str:
        return self.apply_accents_to_text(text, self.get_user_accents(member))

    @Context.hook()
    async def on_send(
        self,
        original: Any,
        ctx: Context,
        content: Any = None,
        *,
        accents: Optional[_UserAccentsType] = None,
        **kwargs: Any,
    ) -> discord.Message:
        if content is not None:
            if accents is None:
                if ctx.guild is not None:
                    accents = self.get_user_accents(ctx.me)  # type: ignore
                else:
                    accents = []

            content = self.apply_accents_to_text(str(content), accents)

        return await original(ctx, content, **kwargs)

    @Context.hook()
    async def on_edit(
        self,
        original: Any,
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
                    accents = self.get_user_accents(ctx.me)  # type: ignore
                else:
                    accents = []

            content = self.apply_accents_to_text(str(content), accents)

        return await original(ctx, message, content=content, **kwargs)

    async def _replace_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if message.guild is None:
            return

        # we are in edit event
        if (old_response := self._sent_webhook_messages.pop(message.id, None)) is not None:
            await self._edit_webhook_message(old_response, message)
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

        if TYPE_CHECKING:
            assert isinstance(message.author, discord.Member)
            # PartialMessageable is weird, it must be excluded by doing this
            assert isinstance(
                message.channel,
                discord.TextChannel | discord.DMChannel | discord.Thread,
            )

        if not (accents := self.get_user_accents(message.author)):
            return

        if not message.channel.permissions_for(message.guild.me).is_superset(REQUIRED_PERMS):
            # NOTE: the decision has been made for this to fail silently.
            # this adds some overhead, but makes bot setup much simplier.
            #
            # TODO: find the other way to tell this to users so that they don't think
            # bot is broken. maybe help text?
            return

        if (ctx := await self.bot.get_context(message)).valid:
            return

        if (content := self.apply_accents_to_text(message.content, accents)) == message.content:
            return

        try:
            new_message = await self._send_new_message(ctx, content, message)
        except discord.NotFound:
            # cached webhook is missing, should invalidate cache
            del self._webhooks[message.channel.id]

            try:
                new_message = await self._send_new_message(ctx, content, message)
            except Exception as e:
                await ctx.reply(
                    f"Accents error: unable to deliver message after invalidating cache: **{e}**.\n"
                    f"Try deleting webhook **{self.accent_wh_name}** manually."
                )

                # NOTE: is it really needed? what else could trigger this?
                # return
                raise

        self._sent_webhook_messages[message.id] = new_message

        with contextlib.suppress(discord.NotFound):
            await message.delete()

    async def _get_cached_webhook(
        self,
        channel: discord.TextChannel,
        create: bool = True,
    ) -> Optional[discord.Webhook]:
        if (wh := self._webhooks.get(channel.id)) is None:
            for wh in await channel.webhooks():
                if wh.name == self.accent_wh_name:
                    break
            else:
                if not create:
                    return None

                wh = await channel.create_webhook(name=self.accent_wh_name)

            self._webhooks[channel.id] = wh

        return wh

    def _copy_embed(self, original: discord.Embed) -> discord.Embed:
        e = original.copy()

        # this results in full sized, but still static image
        #
        # if e.thumbnail:
        #     e.set_image(url=e.thumbnail.url)
        #     e.set_thumbnail(url=e.Empty)

        return e

    async def _send_new_message(
        self,
        ctx: Context,
        content: str,
        original: discord.Message,
    ) -> discord.WebhookMessage:
        return await ctx.send(
            content,
            allowed_mentions=discord.AllowedMentions(
                everyone=original.author.guild_permissions.mention_everyone,  # type: ignore
                users=True,
                roles=True,
            ),
            target=await self._get_cached_webhook(original.channel),  # type: ignore
            register=False,
            accents=[],
            # webhook data
            username=original.author.display_name,
            avatar_url=original.author.display_avatar,
            embeds=list(map(self._copy_embed, original.embeds)),
            wait=True,
        )

    async def _edit_webhook_message(self, original: discord.WebhookMessage, new: discord.Message) -> None:
        # only copy embeds since they arrive late
        await original.edit(embeds=new.embeds)

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        await self._replace_message(message)

    # needed in case people use command and edit their message
    @Cog.listener()
    async def on_message_edit(self, _old: discord.Message, new: discord.Message) -> None:
        # wait for original message to be sent more or less reliably because this edit could be embed edit
        # for that message that should remove original one
        #
        # sleep happens here instead of send for 2 reasons:
        #   - send must be as fast as possible
        #   - embed updates can be quite slow, it is not feasible to wait that long (up to a few seconds)
        await asyncio.sleep(0.5)

        await self._replace_message(new)
