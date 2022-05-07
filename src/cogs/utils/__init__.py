from src.classes.bot import PINK


async def setup(bot: PINK) -> None:
    from .errorhandler import ErrorHandler
    from .responsetracker import ResponseTracker

    await bot.add_cog(ErrorHandler(bot))
    await bot.add_cog(ResponseTracker(bot))
