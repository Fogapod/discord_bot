import os

from typing import Union

import discord

from discord.ext import commands  # type: ignore[attr-defined]

from src.classes.bot import PINK
from src.classes.cog import Cog
from src.classes.context import Context
from src.utils import run_process

from .constants import GIFSICLE_ARGUMENTS
from .flies import draw_flies
from .types import AnimatedImage, Image, StaticImage

try:
    from src.cogs.translator.types import Language
except ImportError:
    raise Exception("This cog relies on the existance of translator cog")

try:
    from src.cogs.accents.types import PINKAccent
except ImportError:
    raise Exception("This cog relies on the existance of accents cog")

from pink_accents import Accent

from .ocr import ocr, ocr_translate


class LanguageOrAccent(commands.Converter):
    async def convert(self, ctx: Context, argument: str) -> Union[str, Accent]:
        try:
            language = await Language.convert(ctx, argument)
        except commands.BadArgument as e:
            try:
                accent = await PINKAccent.convert(ctx, argument)
            except commands.BadArgument:
                raise e

            return accent

        return language


class Images(Cog):
    """
    Image manipulation

    There are multiple ways to provide image arguments.

    If you don't provide text, image is searched in:
      - referenced message attachements/embeds
      - current message atatchments/embeds
      - attachments/embeds in up to 200 messages in history

    If you provide argument, it is checked in the following order:
      - referenced message is checked for attachements/embeds
      - special values (see below)
      - emote/emote id
      - emoji
      - user (id/mention/name/name#discriminator)
      - image URL

    Special values:
      ~ checks history. useful in rare cases when you must provide text
      ^ checks previous message for attachements/embeds. multiple symbols can
        be stacked. each ^ means go 1 message back in history
    """

    @commands.command(hidden=True)
    async def i(
        self,
        ctx: Context,
        i: Image = None,  # type: ignore
    ) -> None:
        if i is None:
            i = await Image.from_history(ctx)

        await ctx.send(i, accents=[])

    @commands.command(hidden=True)
    async def si(
        self,
        ctx: Context,
        i: StaticImage = None,  # type: ignore
    ) -> None:
        if i is None:
            i = await StaticImage.from_history(ctx)

        await ctx.send(i, accents=[])

    @commands.command(hidden=True)
    async def ai(
        self,
        ctx: Context,
        i: AnimatedImage = None,  # type: ignore
    ) -> None:
        if i is None:
            i = await AnimatedImage.from_history(ctx)

        await ctx.send(i, accents=[])

    @commands.command()
    async def ocr(
        self,
        ctx: Context,
        image: Image = None,  # type: ignore
    ) -> None:
        """Read text on image"""

        async with ctx.typing():
            if image is None:
                image = await Image.from_history(ctx)

            annotations = await ocr(ctx, image)

        await ctx.send(f"```\n{annotations['fullTextAnnotation']['text']}```")

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.channel)
    async def trocr(
        self,
        ctx: Context,
        language: LanguageOrAccent,
        image: StaticImage = None,  # type: ignore
    ) -> None:
        """
        Translate text on image

        Note: text rotation is truncated to 90 degrees for now
        Note:
            Entire text is translated at once for the sake of optimization,
            this might produce bad results. This might be improved in future
            (for multi-language images)
        """

        async with ctx.typing():
            if image is None:
                image = await StaticImage.from_history(ctx)

            result, stats = await ocr_translate(ctx, image, language)

        await ctx.send(
            stats,
            file=discord.File(result, filename="trocr.png", spoiler=image.is_spoiler),
        )

    @commands.command(aliases=["flies"])
    @commands.cooldown(1, 12, type=commands.BucketType.channel)
    async def fly(
        self,
        ctx: Context,
        image: StaticImage = None,  # type: ignore
        amount: int = 1,
        fly_image: StaticImage = None,  # type: ignore
    ) -> None:
        """Animates flies on image"""

        if image is None:
            image = await StaticImage.from_history(ctx)

        src = await image.to_pil(ctx)

        if fly_image is not None:
            fly_src = await fly_image.to_pil(ctx)
        else:
            fly_src = None

        min_amount = 1
        max_amount = 50

        if not min_amount <= amount <= max_amount:
            raise commands.BadArgument(f"fly amount should be between **{min_amount}** and **{max_amount}**")

        # TODO: make configurable
        steps = 100
        velocity = 10

        async with ctx.channel.typing():
            filename = await draw_flies(src, fly_src, steps, velocity, amount)

            # optimize gif using gifsicle
            await run_process("gifsicle", *GIFSICLE_ARGUMENTS + [filename])

        await ctx.send(file=discord.File(filename, filename="fly.gif", spoiler=image.is_spoiler))

        os.remove(filename)


async def setup(bot: PINK) -> None:
    await bot.add_cog(Images(bot))
