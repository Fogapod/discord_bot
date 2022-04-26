from __future__ import annotations

import asyncio
import time

from typing import Dict, Optional, Sequence

import discord
import travitia_talk as tt

from discord.ext import commands, tasks  # type: ignore[attr-defined]

from src.bot import PINK
from src.cog import Cog
from src.context import Context
from src.errors import PINKError
from src.settings import BaseSettings, settings

from .types import Emotion

try:
    from src.cogs.accents.types import PINKAccent
except ImportError:
    raise Exception("This cog relies on the existance of accents cog")


class CogSettings(BaseSettings):
    travitia_api_token: str

    class Config(BaseSettings.Config):
        section = "cog.chat"


cog_settings = settings.subsettings(CogSettings)


class SessionSettings:
    __slots__ = (
        "session_id",
        "channel_id",
        "emotion",
        "accents",
        "last_reply",
        "lock",
    )

    def __init__(
        self,
        session_id: int,
        *,
        channel_id: int,
        emotion: tt.Emotion = tt.Emotion.neutral,
        accents: Optional[Sequence[PINKAccent]] = None,
    ):
        self.session_id = session_id
        self.channel_id = channel_id
        self.emotion = emotion

        self.accents = [] if accents is None else accents

        self.last_reply = time.time()
        self.lock = asyncio.Lock()


class Chat(Cog):
    """ChatBot commands"""

    MAX_ACCENTS = 10
    SESSION_RATELIMIT = 3
    SESSION_TIMEOUT = 60

    def __init__(self, bot: PINK):
        super().__init__(bot)

        self.chatbot = tt.ChatBot(cog_settings.travitia_api_token)
        self.emotion = tt.Emotion.neutral

        self.sessions: Dict[int, SessionSettings] = {}

        self.cleanup_sessions.start()

    async def cog_unload(self) -> None:
        self.bot.loop.create_task(self.chatbot.close())

        self.cleanup_sessions.stop()

    @commands.command()
    async def emotion(self, ctx: Context, emotion: Optional[Emotion] = None) -> None:
        """Manage chatbot emotion globally"""

        if emotion is None:
            return await ctx.send(f"Current emotion is **{self.emotion.value}**")

        self.emotion = emotion

        await ctx.ok()

    @commands.command(aliases=["cb", "talk"])
    async def ask(self, ctx: Context, *, text: str) -> None:
        """Talk to bot"""

        async with ctx.typing():
            result = await self._query(text, SessionSettings(ctx.author.id, channel_id=ctx.channel.id))

        await ctx.send(result)

    @commands.command()
    async def session(self, ctx: Context, emotion: Emotion, *accents: PINKAccent) -> None:
        """Start chat session in channel

        Use  accent list  commamd to get list of accents.
        """

        if ctx.author.id in self.sessions:
            del self.sessions[ctx.author.id]

            await ctx.send("Closed previous session")

        if len(accents) > self.MAX_ACCENTS:
            return await ctx.send(f"Cannot use more than {self.MAX_ACCENTS} at once")

        settings = SessionSettings(
            ctx.author.id,
            channel_id=ctx.channel.id,
            emotion=emotion,
            accents=accents,
        )

        self.sessions[ctx.author.id] = settings

        await ctx.send("Started session. Say `stop` to stop")

    async def _query(self, text: str, settings: SessionSettings) -> str:
        lower_bound = 3
        upper_bound = 60

        if not (lower_bound <= len(text) <= upper_bound):
            return f"Error: Text lenght must be between **{lower_bound}** and **{upper_bound}**"

        try:
            response = await self.chatbot.ask(text, id=settings.session_id, emotion=settings.emotion)
        except tt.APIError as e:
            # let sentry catch it
            raise PINKError(f"Error: `{e}`")

        return response.text

    @tasks.loop(minutes=5)
    async def cleanup_sessions(self) -> None:
        now = time.time()

        expired = []

        for user_id, session_settings in self.sessions.items():
            if session_settings.lock.locked():
                continue

            if (now - session_settings.last_reply) > self.SESSION_TIMEOUT:
                expired.append(user_id)

        for user_id in expired:
            del self.sessions[user_id]

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.id not in self.sessions:
            return

        settings = self.sessions[message.author.id]
        if settings.channel_id != message.channel.id:
            return

        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        if message.content.lower() == "stop":
            del self.sessions[message.author.id]

            return await ctx.send("Closed session")

        if (time.time() - settings.last_reply) < self.SESSION_RATELIMIT:
            await ctx.reply("You are sending messages too frequently")
            return

        if settings.lock.locked():
            return

        async with settings.lock:
            async with ctx.typing():
                result = await self._query(message.content, settings)

                await ctx.reply(result, accents=settings.accents)

            settings.last_reply = time.time()


async def setup(bot: PINK) -> None:
    await bot.add_cog(Chat(bot))
