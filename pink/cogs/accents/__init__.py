from pink.bot import PINK


async def setup(bot: PINK) -> None:
    # this is required to not overwrite hook decorator declarations each time other cogs import from accents
    from .cog import Accents

    await bot.add_cog(Accents(bot))
