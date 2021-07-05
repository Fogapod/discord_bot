import discord

from discord.ext import commands

from pink.bot import Bot
from pink.cog import Cog
from pink.context import Context

from .ocr import ocr, trocr
from .types import Image, StaticImage, AnimatedImage

try:
    from pink.cogs.translator.types import Language
except ImportError:
    raise Exception("This cog relies on the existance of translator cog")


class Images(Cog):
    """Image manipulation"""

    @commands.command(hidden=True)
    async def i(self, ctx: Context, i: Image = None) -> None:
        if i is None:
            i = await Image.from_history(ctx)

        await ctx.send(i, accents=[])

    @commands.command(hidden=True)
    async def si(self, ctx: Context, i: StaticImage = None) -> None:
        if i is None:
            i = await StaticImage.from_history(ctx)

        await ctx.send(i, accents=[])

    @commands.command(hidden=True)
    async def ai(self, ctx: Context, i: AnimatedImage = None) -> None:
        if i is None:
            i = await AnimatedImage.from_history(ctx)

        await ctx.send(i, accents=[])

    @commands.command()
    async def ocr(self, ctx: Context, image: Image = None) -> None:
        """Read text on image"""

        if image is None:
            image = await Image.from_history(ctx)

        annotations = await ocr(ctx, image.url)

        await ctx.send(f"```\n{annotations['fullTextAnnotation']['text']}```")

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 5, type=commands.BucketType.channel)
    async def trocr(
        self, ctx: Context, language: Language, image: StaticImage = None
    ) -> None:
        """
        Translate text on image

        Note: text rotation is truncated to 90 degrees for now
        Note:
            Entire text is translated at once for the sake of optimization,
            this might produce bad results. This might be improved in future
            (for multi-language images)
        """

        if image is None:
            image = await StaticImage.from_history(ctx)

        result, stats = await trocr(ctx, image, language)

        await ctx.send(stats, file=discord.File(result, filename="trocr.png"))


def setup(bot: Bot) -> None:
    bot.add_cog(Images(bot))
