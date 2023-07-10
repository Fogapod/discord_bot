import logging
import random

from typing import Optional, Union

import discord

from discord.ext import commands

from src.bot import PINK
from src.cog import Cog
from src.context import Context

log = logging.getLogger(__name__)


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


async def setup(bot: PINK) -> None:
    await bot.add_cog(Fun(bot))
