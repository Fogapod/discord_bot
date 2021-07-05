import re

from discord.ext import commands
from pink_accents import Accent

from pink.context import Context

from .constants import ALL_ACCENTS


# inherit to make linters sleep well
class PINKAccent(Accent, register=False):
    MIN_SEVERITY = 1
    MAX_SEVERITY = 10

    @classmethod
    async def convert(cls, ctx: Context, argument: str) -> Accent:
        match = re.match(r"(.+?)(:?\[(\d+)\])?$", argument)
        assert match

        name = match[1]
        severity = 1 if match[3] is None else int(match[3])

        prepared = name.replace(" ", "_").lower()
        try:
            accent = ALL_ACCENTS[prepared]
        except KeyError:
            raise commands.BadArgument(f'Accent "{name}" does not exist')

        if not (cls.MIN_SEVERITY <= severity <= cls.MAX_SEVERITY):
            raise commands.BadArgument(
                f"{accent}: severity must be between {cls.MIN_SEVERITY} and {cls.MAX_SEVERITY}"
            )

        return accent(severity)
