from __future__ import annotations

import inspect

from typing import Any

from discord.ext import commands

from .bot import Bot


class Cog(commands.Cog):
    def __new__(cls, *args: Any, **kwargs: Any) -> Cog:
        self = super().__new__(cls, *args, **kwargs)

        hooks = []

        for base in cls.__mro__:
            for value in base.__dict__.values():
                if inspect.iscoroutinefunction(value):
                    if hasattr(value, "__hook_target__"):
                        hooks.append(value)

        self.__cog_hooks__ = hooks

        return self

    def __init__(self, bot: Bot):
        self.bot = bot

        self.bot.loop.create_task(self._setup())

    async def _setup(self) -> None:
        await self.bot.wait_until_ready()

        await self.setup()

    async def setup(self) -> None:
        pass

    def cog_unload(self) -> None:
        for hook in self.__cog_hooks__:
            hook.__hook_target__.remove_hook(hook)
