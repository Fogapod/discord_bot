from discord.ext import commands

from .bot import PINK

__all__ = ("Cog",)


class Cog(commands.Cog):
    def __init__(self, bot: PINK):
        self.bot = bot
