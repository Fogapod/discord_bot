import logging
import random

from collections.abc import Iterable, Iterator, Sequence
from typing import Optional, TypeVar, Union

import discord

from discord.ext import commands

from src.bot import PINK
from src.cog import Cog
from src.context import Context
from src.errors import PINKError

log = logging.getLogger(__name__)

T = TypeVar("T")


class Fun(Cog):
    """Commands without practical use"""

    THROWABLE_ITEMS = (
        "dead bird",
        "potato",
        "rock",
        "stick",
        "divorce papers",
        "dice",
        "weird look",
        "sock",
        "apple",
        "car keys",
        "chair",
        "hamburger",
        "clownburger",
        "kitty ears",
        "o2 tank",
        "normal looking pen",
        "a water bucket",
        "a pair of shoes",
        "lizard",
        "beer",
        "poorly written computer program",
        "water balloon",
        "nothing",
        "chessboard",
        "bowl of rice",
        "mug",
        "mud",
        "egg",
        "up",
        "spear",
        "pea",
        "curses",
        "snowball",
        "sand",
        "soap",
    )

    @commands.command()
    async def throw(
        self,
        ctx: Context,
        target: Optional[
            Union[
                discord.User,
                discord.TextChannel,
                discord.CategoryChannel,
                discord.VoiceChannel,
                str,
            ]
        ] = None,
        *,
        item: Optional[str] = None,
    ) -> None:
        """Throw things, for FUN

        Target can be user, channel or just string.
        You can also attach file as target."""

        if target is None:
            if isinstance(ctx.channel, discord.DMChannel):
                target = random.choice((ctx.me, ctx.author))  # type: ignore
            else:
                target = random.choice(ctx.channel.members)  # type: ignore

        preposition = "at"

        if isinstance(target, discord.User):
            if target in ctx.message.mentions:
                mention = target.mention
            else:
                mention = f"`{target}`"

        elif isinstance(
            target,
            discord.TextChannel | discord.CategoryChannel | discord.VoiceChannel,
        ):
            mention = target.mention
            preposition = "into"
        else:
            mention = target  # type: ignore

        if item is None:
            if ctx.message.attachments:
                item = ctx.message.attachments[0].url
            else:
                item = random.choice(self.THROWABLE_ITEMS)

        verb = random.choice(
            (
                "throws",
                "threw",
                "is throwing",
            )
        )

        modifier = random.choice(
            (
                "",
                " angrily",
                " lazily",
                " weakly",
                " with a great force",
                ", aiming for the kill",
                " and misses!!",
            )
        )

        await ctx.send(f"**{ctx.author}** {verb} {item} {preposition} **{mention}**{modifier}!")

        if isinstance(target, discord.TextChannel):
            if (
                target.guild == ctx.guild
                and target.permissions_for(ctx.author).send_messages  # type: ignore
                and target.permissions_for(ctx.me).send_messages  # type: ignore
            ):
                if ctx.channel.is_nsfw() and not target.is_nsfw():  # type: ignore
                    return await ctx.send("Can't throw items from horny channel!")

                return await ctx.send(
                    f"{item} flies from `{ctx.author}` in {ctx.channel.mention}!",  # type: ignore
                    target=target,
                    allowed_mentions=discord.AllowedMentions(users=False),
                )

            await ctx.send(f"{item} bounces back from {mention} and hits `{ctx.author}`!")

    @commands.command()
    async def say(self, ctx: Context, *, text: str) -> None:
        """Make bot say something"""

        await ctx.send(text)

    # it is not very fun because there is no way to distinguish between people with accents / matrix bridged folks
    # and impersonated messages
    # disable for now, might remove later
    @commands.command(aliases=["pretend"], enabled=False)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def impersonate(self, ctx: Context, user: Union[discord.Member, discord.User], *, text: str) -> None:
        """Send message as someone else"""

        name = user.display_name[:32]

        # webhook names cannot be shorter than 2
        if len(name) < 2:
            name = f"\u200b{name}"

        accents = []

        if isinstance(user, discord.Member):
            if (accent_cog := ctx.bot.get_cog("Accents")) is None:
                log.warning("accents cog not found, cannot apply accents to impersonation")
            else:
                if user_accents := accent_cog.get_user_accents(user):  # type: ignore
                    accents = user_accents

        try:
            webhook = await ctx.channel.create_webhook(name="PINK impersonation webhook")  # type: ignore
        except Exception as e:
            await ctx.reply(f"Unable to create webhook: {e}")

            return

        try:
            await ctx.send(
                text,
                target=webhook,
                username=name,
                avatar_url=user.display_avatar.with_format("png"),
                wait=True,
                accents=accents,
            )
        except Exception as e:
            await ctx.reply(f"Unable to send message: {e}")
        finally:
            await webhook.delete()

    @commands.command()
    @commands.cooldown(1, 2, type=commands.BucketType.user)
    async def randmsg(self, ctx: Context, channel: discord.TextChannel = commands.parameter(default=None)) -> None:
        """
        Returns random message from channel
        """

        if channel is None:
            channel = ctx.channel

        self._ensure_fetch_perms(ctx.author, channel)
        past_point = await self._random_history_point(ctx.message, channel)

        # not sure if around always work. if this ever errors, use before/after
        random_message = [m async for m in channel.history(limit=1, around=past_point)][0]

        if channel == ctx.channel:
            await ctx.send(
                f"by **{random_message.author}** in {random_message.created_at.year}",
                mention_author=False,
                reference=random_message,
            )
        else:
            await ctx.reply(
                f"by **{random_message.author}** in {random_message.created_at.year}: {random_message.jump_url}",
                mention_author=False,
                # we can not afford to fuck up jump url with owo or something
                accents=[],
            )

    @staticmethod
    def _ensure_fetch_perms(user: discord.User | discord.Member, channel: discord.TextChannel) -> None:
        user_perms = channel.permissions_for(user)  # type: ignore
        if not (user_perms.read_messages and user_perms.read_message_history):
            raise PINKError(f"You do not have access to {channel.mention}")

        my_perms = channel.permissions_for(user)  # type: ignore
        if not (my_perms.read_messages and my_perms.read_message_history):
            raise PINKError(f"I do not have access to {channel.mention}")

    @staticmethod
    async def _random_history_point(
        present: discord.Message,
        channel: discord.TextChannel | discord.DMChannel,
    ) -> discord.Object:
        # this should never index error because we at least should have initial message in channel
        # might be worth caching this
        oldest = [m async for m in channel.history(limit=1, oldest_first=True)][0]

        if present == oldest:
            offset = 0
        else:
            diff = present.id - oldest.id
            offset = random.randrange(diff)

        return discord.Object(id=oldest.id + offset)

    @commands.command()
    @commands.cooldown(1, 4, type=commands.BucketType.user)
    async def randimg(self, ctx: Context, channel: discord.TextChannel = commands.parameter(default=None)) -> None:
        """
        Returns random image from channel
        """

        if channel is None:
            channel = ctx.channel

        if isinstance(channel, discord.TextChannel) and channel.is_nsfw() and not ctx.channel.nsfw:  # type: ignore
            raise PINKError("Tried getting image from NSFW channel into SFW")

        self._ensure_fetch_perms(ctx.author, channel)
        past_point = await self._random_history_point(ctx.message, channel)

        middle = [m async for m in channel.history(limit=101, around=past_point)]

        if (maybe_image := self._find_image(self.spiral_out(middle))) is None:
            # TODO: expand to left and right from here bt fetching 200 messages at a time and doing spiral
            raise PINKError("Could not find any images")

        url, spoiler = maybe_image
        if spoiler:
            url = f"|| {url} ||"

        await ctx.reply(url, mention_author=False, accents=[])

    @staticmethod
    def _find_image(messages: Iterable[discord.Message]) -> Optional[tuple[str, bool]]:
        """Returns as soon as it hits image"""

        for message in messages:
            candidates = []

            for attachment in message.attachments:
                extension = attachment.filename.rpartition(".")[-1].lower()
                if extension in ("png", "jpg", "jpeg", "webp"):
                    candidates.append((attachment.url, attachment.is_spoiler()))

            for embed in message.embeds:
                if embed.image and embed.image.url:
                    candidates.append((embed.image.url, False))

                if embed.thumbnail and embed.thumbnail.url:
                    candidates.append((embed.thumbnail.url, False))

            if candidates:
                return random.choice(candidates)

        return None

    @staticmethod
    def spiral_out(arr: Sequence[T]) -> Iterator[T]:
        middle = len(arr) // 2

        sign = -1

        for i in range(1, len(arr) + 1):
            sign *= -1

            yield arr[middle + i // 2 * sign]


async def setup(bot: PINK) -> None:
    await bot.add_cog(Fun(bot))
