from discord.ext import commands

from pink.context import Context

from .constants import LANGCODES, LANGUAGES, LANGCODE_ALIASES


class Language(str):
    @classmethod
    async def convert(cls, _: Context, argument: str) -> str:
        argument = argument.lower()

        code = LANGCODES.get(argument, argument)

        if (maybe_alias := LANGCODE_ALIASES.get(code, code)) not in LANGUAGES:
            raise commands.BadArgument(
                "Invalid language. Use `tr list` to get list of supported languages"
            )

        return maybe_alias
