from typing import Any, Union, Optional

import edgedb
import aiohttp
import discord

from discord.ext import commands

from .hookable import AsyncHookable


class CTXExit(Exception):
    """
    A special type of exception used for exiting nested contexts.
    Error handler should ignore this exception
    """

    def __init__(self, message: Optional[discord.Message] = None):
        self.message = message


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
        target: discord.abc.Messageable = None,
        exit: bool = False,
        **kwargs: Any,
    ) -> discord.Message:
        if target is None:
            message = await super().send(content, **kwargs)
        else:
            message = await target.send(content, **kwargs)

        if exit:
            raise CTXExit(message=message)

        return message

    async def reply(self, content: Any = None, **kwargs: Any) -> discord.Message:
        return await self.send(content, reference=self.message, **kwargs)

    @AsyncHookable.hookable()
    async def edit(
        self,
        message: discord.Message,
        *,
        content: Any = None,
        exit: bool = False,
        **kwargs: Any,
    ) -> None:

        await message.edit(content=content, **kwargs)

        if exit:
            raise CTXExit()

    @AsyncHookable.hookable()
    async def react(
        self,
        emoji: Union[discord.Emoji, str],
        message: discord.Message = None,
        *,
        exit: bool = False,
    ) -> discord.Message:
        if message is None:
            message = self.message

        await message.add_reaction(emoji)

        if exit:
            raise CTXExit(message=message)

        return message

    async def ok(self, message: discord.Message = None) -> discord.Message:
        if message is None:
            message = self.message

        return await self.react("\N{HEAVY CHECK MARK}", message=message)

    async def nope(self, message: discord.Message = None) -> discord.Message:
        if message is None:
            message = self.message

        return await self.react("\N{HEAVY MULTIPLICATION X}", message=message)
