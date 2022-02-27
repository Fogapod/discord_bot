from typing import Any, Optional, Union

import aiohttp
import discord
import edgedb

from discord.ext import commands  # type: ignore[attr-defined]

from .hookable import AsyncHookable


class Context(commands.Context, AsyncHookable):
    @property
    def prefix(self) -> str:
        return self._prefix  # type: ignore

    @prefix.setter
    def prefix(self, value: Optional[str]) -> None:
        # because custom get_prefix can leave spaces
        self._prefix = None if value is None else value.rstrip()

    @property
    def edb(self) -> edgedb.AsyncIOPool:
        return self.bot.edb

    @property
    def session(self) -> aiohttp.ClientSession:
        return self.bot.session

    @AsyncHookable.hookable()
    async def send(
        self,
        content: Any = None,
        *,
        target: Optional[discord.abc.Messageable] = None,
        **kwargs: Any,
    ) -> discord.Message:

        if target is None:
            # mypy does not recognize superclass here and just names it "super"
            target = super()  # type: ignore[assignment]
            assert target is not None

        if content is not None:
            # hardcoded 2000 limit because error handling is tricky with 50035
            # and this project is EOL
            content = str(content)[:2000]

        return await target.send(content, **kwargs)

    async def reply(self, content: Any = None, **kwargs: Any) -> discord.Message:
        return await self.send(content, reference=self.message, **kwargs)

    @AsyncHookable.hookable()
    async def edit(
        self,
        message: discord.Message,
        *,
        content: Any = None,
        **kwargs: Any,
    ) -> None:

        await message.edit(content=content, **kwargs)

    @AsyncHookable.hookable()
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
