import itertools
import logging
import random

from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Optional

import discord

from discord.ext import commands
from discord.ext.commands import MessageConverter

from src.bot import PINK
from src.cog import Cog
from src.context import Context
from src.errors import PINKError

log = logging.getLogger(__name__)

IMAGE_FORMATS = {"png", "jpg", "jpeg", "webp", "gif"}


class DateConverter:
    """Converts string to datetime"""

    @classmethod
    async def convert(cls, _: Context, argument: str) -> datetime:
        for pattern in ("%Y", "%Y-%m", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(argument, pattern)
            except ValueError:
                continue

            return parsed.replace(tzinfo=timezone.utc)

        raise ValueError("Could not parse date")


class MessageDateConverter(MessageConverter):
    """Takes date out of message"""

    async def convert(self, ctx: Context, argument: str) -> datetime:  # type: ignore
        msg = await super().convert(ctx, argument)

        return msg.created_at


class RandItemFlags(commands.FlagConverter, delimiter=" ", prefix="--"):
    before: datetime = commands.flag(
        default=lambda ctx: ctx.message.created_at,
        converter=Optional[MessageDateConverter | DateConverter],
    )
    after: Optional[datetime] = commands.flag(
        converter=Optional[MessageDateConverter | DateConverter],
    )


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
            discord.User | discord.TextChannel | discord.CategoryChannel | discord.VoiceChannel | str
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
                if ctx.channel.nsfw > target.nsfw:  # type: ignore
                    return await ctx.send("Can't throw items from horny channel!")

                return await ctx.send(
                    f"{item} flies from `{ctx.author}` in {ctx.channel.mention}!",  # type: ignore
                    target=target,
                    allowed_mentions=discord.AllowedMentions(users=False),
                )

            await ctx.send(f"{item} bounces back from {mention} and hits `{ctx.author}`!")

    @commands.command()
    async def scramble(self, ctx: Context, *, text: Optional[str]) -> None:
        """Scramble words in text"""

        if text is None:
            if (reference := ctx.message.reference) is None:
                await ctx.reply("Give text or reference a message")

                return

            if not isinstance(reference.resolved, discord.Message):
                await ctx.reply("Referenced message is either deleted or not cached")

                return

            text = reference.resolved.content

        words: defaultdict[int, str] = defaultdict(str)
        special: defaultdict[int, str] = defaultdict(str)

        in_special = False
        i = 0
        for c in text:
            if c.isalnum():
                if in_special:
                    in_special = False
                    i += 1
                words[i] += c
            else:
                if not in_special:
                    in_special = True
                    i += 1
                special[i] += c

        word_was_first = words and next(iter(words)) == 0

        words_list = random.sample(list(words.values()), k=len(words))
        special_list = special.values()

        first, second = (words_list, special_list) if word_was_first else (special_list, words_list)
        await ctx.send("".join(itertools.chain(*itertools.zip_longest(first, second, fillvalue=""))))

    @commands.command()
    async def scramble2(self, ctx: Context, *, text: Optional[str]) -> None:
        """Scramble words of same lengths in text"""

        if text is None:
            if (reference := ctx.message.reference) is None:
                await ctx.reply("Give text or reference a message")

                return

            if not isinstance(reference.resolved, discord.Message):
                await ctx.reply("Referenced message is either deleted or not cached")

                return

            text = reference.resolved.content

        words: defaultdict[int, str] = defaultdict(str)
        special: defaultdict[int, str] = defaultdict(str)

        in_special = False
        i = 0
        for c in text:
            if c.isalnum():
                if in_special:
                    in_special = False
                    i += 1
                words[i] += c
            else:
                if not in_special:
                    in_special = True
                    i += 1
                special[i] += c

        word_was_first = words and next(iter(words)) == 0

        # TODO: itertools.groupby maybe
        lengths = defaultdict(list)
        for i, word in words.items():
            lengths[len(word)].append((i, word))

        for group in lengths.values():
            if len(group) == 1:
                continue

            indexes = [i for i, _ in group]
            group_words = [w for _, w in group]

            for i, word in zip(indexes, random.sample(group_words, k=len(group_words))):
                # replace and copy case for each letter from old value
                words[i] = "".join(
                    [c_new.upper() if c_old.isupper() else c_new.lower() for c_new, c_old in zip(word, words[i])]
                )

        words_list = words.values()
        special_list = special.values()

        first, second = (words_list, special_list) if word_was_first else (special_list, words_list)
        await ctx.send("".join(itertools.chain(*itertools.zip_longest(first, second, fillvalue=""))))

    @commands.command()
    async def say(self, ctx: Context, *, text: str) -> None:
        """Make bot say something"""

        await ctx.send(text)

    # it is not very fun because there is no way to distinguish between people with accents / matrix bridged folks
    # and impersonated messages
    # disable for now, might remove later
    @commands.command(aliases=["pretend"], enabled=False)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def impersonate(self, ctx: Context, user: discord.Member | discord.User, *, text: str) -> None:
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

    @commands.command(aliases=["randm"])
    @commands.cooldown(1, 2, type=commands.BucketType.user)
    async def randmsg(
        self,
        ctx: Context,
        channel: discord.TextChannel = commands.parameter(
            # note: commands.CurrentChannel is broken here for some reason. it returns parameter object
            default=lambda ctx: ctx.channel,
            description="channel to use",
            displayed_default="current channel",
        ),
        *,
        flags: RandItemFlags = commands.parameter(description="additional flags"),
    ) -> None:
        """
        Returns random message from channel

        Supports additional flags --before and --after which could be either message link or date in YYYY-MM-DD format.
        """

        self._ensure_fetch_perms(ctx.me, ctx.author, channel)

        before = flags.before
        after = flags.after
        past_point = await self._random_history_point(channel, before, after=after)

        middle = [m async for m in channel.history(limit=101, around=past_point, before=before, after=after)]
        if not middle:
            raise PINKError("No messages in given interval")

        random_message = random.choice(middle)

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
    def _ensure_fetch_perms(
        me: discord.ClientUser | discord.Member,
        user: discord.User | discord.Member,
        channel: discord.TextChannel,
    ) -> None:
        user_perms = channel.permissions_for(user)  # type: ignore
        if not (user_perms.read_messages and user_perms.read_message_history):
            raise PINKError(f"You do not have access to {channel.mention}")

        my_perms = channel.permissions_for(me)  # type: ignore
        if not (my_perms.read_messages and my_perms.read_message_history):
            raise PINKError(f"I do not have access to {channel.mention}")

    @staticmethod
    async def _random_history_point(
        channel: discord.TextChannel | discord.DMChannel,
        before: datetime,
        after: Optional[datetime] = None,
    ) -> discord.Object:
        if after is None:
            after_id = channel.id
        else:
            after_id = discord.utils.time_snowflake(after) - 1

        before_id = discord.utils.time_snowflake(before) - 1

        # randrange needs at least 1 step difference
        before_id += 1

        if before_id < after_id:
            raise PINKError("After is older than before")

        return discord.Object(id=random.randrange(after_id, before_id))

    @commands.command(aliases=["randi"])
    @commands.cooldown(1, 2, type=commands.BucketType.user)
    async def randimg(
        self,
        ctx: Context,
        channel: discord.TextChannel = commands.parameter(
            default=lambda ctx: ctx.channel,
            description="channel to use",
            displayed_default="current channel",
        ),
        *,
        flags: RandItemFlags = commands.parameter(description="additional flags"),
    ) -> None:
        """
        Returns random image from channel

        Supports additional flags --before and --after which could be either message link or date in YYYY-MM-DD format.
        """

        self._ensure_fetch_perms(ctx.me, ctx.author, channel)

        if isinstance(channel, discord.TextChannel) and channel.nsfw > ctx.channel.nsfw:  # type: ignore
            raise PINKError("Tried getting image from NSFW channel into SFW")

        before = flags.before
        after = flags.after
        past_point = await self._random_history_point(channel, before, after=after)

        middle = [m async for m in channel.history(limit=101, around=past_point, before=before, after=after)]
        if not middle:
            raise PINKError("No messages in given interval")

        if not (candidates := self._find_images(middle)):
            # TODO: expand to left and right from here by fetching 200 messages at a time and spiraling joined array
            raise PINKError("Could not find any images (101)")

        # same as randmsg: do not pick first
        url, spoiler = random.choice(candidates)
        if spoiler:
            url = f"|| {url} ||"

        await ctx.reply(url, mention_author=False, accents=[])

    @staticmethod
    def _find_images(messages: Iterable[discord.Message]) -> list[tuple[str, bool]]:
        """Returns all images"""

        candidates = []

        for message in messages:
            for attachment in message.attachments:
                extension = attachment.filename.rpartition(".")[-1].lower()
                if extension in IMAGE_FORMATS:
                    candidates.append((attachment.url, attachment.is_spoiler()))

            for embed in message.embeds:
                if embed.image and embed.image.url:
                    candidates.append((embed.image.url, False))

                if embed.thumbnail and embed.thumbnail.url:
                    candidates.append((embed.thumbnail.url, False))

        return candidates

    @commands.command(aliases=["randa"])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def randatt(
        self,
        ctx: Context,
        channel: discord.TextChannel = commands.parameter(
            default=lambda ctx: ctx.channel,
            description="channel to use",
            displayed_default="current channel",
        ),
        *,
        flags: RandItemFlags = commands.parameter(description="additional flags"),
    ) -> None:
        """
        Returns random non-image attachment from channel.

        Supports additional flags --before and --after which could be either message link or date in YYYY-MM-DD format.
        """

        self._ensure_fetch_perms(ctx.me, ctx.author, channel)

        if isinstance(channel, discord.TextChannel) and channel.nsfw > ctx.channel.nsfw:  # type: ignore
            raise PINKError("Tried getting attachment from NSFW channel into SFW")

        before = flags.before
        after = flags.after
        past_point = await self._random_history_point(channel, before, after=after)

        # checks up to 701 messages with up to 7 history calls
        middle = [m async for m in channel.history(limit=101, around=past_point, before=before, after=after)]
        if not middle:
            raise PINKError("No messages in given interval")

        if candidates := await self._find_attachments(middle):
            attachment = random.choice(candidates)
            await ctx.reply(
                file=await attachment.to_file(spoiler=attachment.is_spoiler()),
                mention_author=False,
                accents=[],
            )
            return

        checked_messages = 101

        # middle failed, spiral out by fetching left and right sides of history
        for _ in range(3):
            left = [m async for m in channel.history(limit=100, before=middle[0], after=after)]
            right = [m async for m in channel.history(limit=100, after=middle[-1], before=before)]
            middle = [*left, *right]

            if candidates := await self._find_attachments(middle):
                attachment = random.choice(candidates)
                await ctx.reply(
                    file=await attachment.to_file(spoiler=attachment.is_spoiler()),
                    mention_author=False,
                    accents=[],
                )
                return

            checked_messages += len(middle)

            # one or both sides hit channel end
            if len(middle) < 200:
                break

        raise PINKError(f"Could not find any attachemnts ({checked_messages})")

    @staticmethod
    async def _find_attachments(messages: Iterable[discord.Message]) -> list[discord.Attachment]:
        """Returns all non-image attachments"""

        candidates = []
        for message in messages:
            for attachment in message.attachments:
                extension = attachment.filename.rpartition(".")[-1].lower()
                if extension in IMAGE_FORMATS:
                    continue

                candidates.append(attachment)

        return candidates


async def setup(bot: PINK) -> None:
    await bot.add_cog(Fun(bot))
