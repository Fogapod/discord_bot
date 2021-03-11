import logging

import sentry_sdk

from discord.ext import commands

from potato_bot.bot import Bot
from potato_bot.cog import Cog
from potato_bot.context import Context, CTXExit

log = logging.getLogger(__name__)


class ErrorHandler(Cog):
    @Cog.listener()
    async def on_command_error(self, ctx: Context, e: Exception) -> None:
        if isinstance(e, commands.CommandInvokeError):
            e = e.original

        ignored = (
            commands.CommandNotFound,
            CTXExit,
        )
        if isinstance(e, ignored):
            return

        if isinstance(e, commands.MissingRole):
            if isinstance(e.missing_role, int):
                role = f"<@&{e.missing_role}>"
            else:
                role = f"named **{e.missing_role}**"

            await ctx.reply(f"You must have {role} role to use this")
        elif isinstance(e, commands.CheckFailure):
            # all other checks
            error = str(e)
            if not error:
                error = f"**{e.__class__.__name__}**"

            await ctx.reply(f"Check failed: {error}")
        elif isinstance(
            e,
            (
                commands.MissingRequiredArgument,
                commands.BadArgument,
                commands.NoPrivateMessage,
            ),
        ):
            await ctx.reply(f"Error: **{e}**")
        elif isinstance(e, commands.TooManyArguments):
            await ctx.send_help(ctx.command)
        elif isinstance(e, (commands.ArgumentParsingError, commands.BadUnionArgument)):
            await ctx.reply(f"Unable to process command arguments: {e}")
        else:
            await ctx.reply(f"Unexpected error: **{type(e).__name__}**: `{e}`")

            sentry_sdk.capture_exception(e)

            raise e


def setup(bot: Bot) -> None:
    bot.add_cog(ErrorHandler(bot))
