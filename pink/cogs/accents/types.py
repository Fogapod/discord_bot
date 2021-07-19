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
        match = re.fullmatch(r"(.+?)(:?\[(\d{1,2})\])?", argument)
        assert match

        name = match[1].lower()
        severity = 1 if match[3] is None else int(match[3])

        try:
            accent = ALL_ACCENTS[name.lower()]
        except KeyError:
            raise commands.BadArgument(f"not a valid accent: {name}")

        if not (cls.MIN_SEVERITY <= severity <= cls.MAX_SEVERITY):
            raise commands.BadArgument(
                f"{accent.name}: severity must be between {cls.MIN_SEVERITY} and {cls.MAX_SEVERITY}"
            )

        return accent(severity)
