import logging
import traceback

from discord.ext import commands  # type: ignore[attr-defined]

from .bot import PINK
from .hooks import HookHost

log = logging.getLogger(__name__)


class Cog(commands.Cog, HookHost):
    def __init__(self, bot: PINK):
        self.bot = bot

        self.bot.loop.create_task(self._setup())

    async def _setup(self) -> None:
        await self.bot.wait_until_ready()

        try:
            await self.setup()
        except Exception as e:
            log.error(f"Error setting up {self.__module__}: {type(e).__name__} - {e}")
            traceback.print_exc()

            self.bot.unload_extension(self.__module__)

    async def setup(self) -> None:
        pass

    def cog_unload(self) -> None:
        self.unregister_hooks()
