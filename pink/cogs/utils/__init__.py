from pink.bot import PINK


def setup(bot: PINK) -> None:
    from .errorhandler import ErrorHandler
    from .responsetracker import ResponseTracker

    bot.add_cog(ErrorHandler(bot))
    bot.add_cog(ResponseTracker(bot))
