from pink.bot import PINK


def setup(bot: PINK) -> None:
    # this is required to not overwrite hook decorator declarations each time other cogs import from accents
    from .cog import Accents

    bot.add_cog(Accents(bot))
