from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

import aiohttp
import asyncpg
import discord

from discord.ext import commands  # type: ignore[attr-defined]

from .hooks import Hookable

if TYPE_CHECKING:
    from .bot import PINK

__all__ = ("Context",)


class Context(commands.Context, Hookable):
    bot: PINK

    @property
    def prefix(self) -> Optional[str]:
        return self._prefix

    @prefix.setter
    def prefix(self, value: Optional[str]) -> None:
        # because custom get_prefix can leave spaces
        self._prefix = None if value is None else value.rstrip()

    @property
    def pg(self) -> asyncpg.Pool[asyncpg.Record]:
        return self.bot.pg

    @property
    def session(self) -> aiohttp.ClientSession:
        return self.bot.session

    @Hookable.hookable()
    async def send(
        self,
        content: Any = None,
        *,
        target: Optional[discord.abc.Messageable] = None,
        **kwargs: Any,
    ) -> discord.Message:

        if target is None:
            target = super()

            # mypy does not recognize superclass here and just names it "super"
            if TYPE_CHECKING:
                assert isinstance(target, discord.abc.Messageable)

        if content is not None:
            # hardcoded 2000 limit because error handling is tricky with 50035
            # and this project is EOL
            content = str(content)[:2000]

        return await target.send(content, **kwargs)

    async def reply(self, content: Any = None, **kwargs: Any) -> discord.Message:
        return await self.send(content, reference=self.message, **kwargs)

    @Hookable.hookable()
    async def edit(
        self,
        message: discord.Message,
        *,
        content: Any = None,
        **kwargs: Any,
    ) -> None:

        await message.edit(content=content, **kwargs)

    @Hookable.hookable()
    async def react(
        self,
        emoji: Union[discord.Emoji, str],
        message: Optional[discord.Message] = None,
    ) -> discord.Message:
        if message is None:
            message = self.message

        await message.add_reaction(emoji)

        return message

    async def ok(self, message: Optional[discord.Message] = None) -> discord.Message:
        if message is None:
            message = self.message

        return await self.react("\N{HEAVY CHECK MARK}", message=message)

    async def nope(self, message: Optional[discord.Message] = None) -> discord.Message:
        if message is None:
            message = self.message

        return await self.react("\N{HEAVY MULTIPLICATION X}", message=message)
