from __future__ import annotations

import io
import sqlite3

from typing import TYPE_CHECKING, Any, Optional

import aiohttp
import discord

from discord.ext import commands
from redis.asyncio import Redis

from src.hooks import Hookable

if TYPE_CHECKING:
    from .bot import PINK

__all__ = ("Context",)


class Context(commands.Context[PINK], Hookable):
    @property
    def prefix(self) -> Optional[str]:
        return self._prefix

    @prefix.setter
    def prefix(self, value: Optional[str]) -> None:
        # because custom get_prefix can leave spaces
        self._prefix = None if value is None else value.rstrip()

    @property
    def db(self) -> sqlite3.Cursor:
        return self.bot.db_cursor()

    @property
    def redis(self) -> Redis[bytes]:
        return self.bot.redis

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
            # mypy does not recognize superclass here and just names it "super"
            target = super()  # type: ignore

            if TYPE_CHECKING:
                assert isinstance(target, discord.abc.Messageable)

        try:
            return await target.send(content, **kwargs)
        except discord.HTTPException as e:
            # message content too long (default limit is 2000)
            if e.code == 50035:
                if len(files := kwargs.pop("files", [])) == 10:
                    # custom error perhaps?
                    return await target.send(str(content)[:2000], **kwargs)

                files.append(discord.File(io.StringIO(str(content)), filename="message.txt"))  # type: ignore[arg-type]

                return await target.send(files=files, **kwargs)

            raise

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
        emoji: discord.Emoji | str,
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
