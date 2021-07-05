from discord.ext import commands
from googletrans import LANGCODES, LANGUAGES

from pink.context import Context


class Language(str):
    @classmethod
    async def convert(cls, ctx: Context, argument: str) -> str:
        language = argument.lower()

        language = LANGCODES.get(language, language)
        if language not in LANGUAGES:
            ctx.command.reset_cooldown(ctx)

            raise commands.BadArgument(
                "Invalid language. Use `tr list` to get list of supported languages"
            )

        return language
