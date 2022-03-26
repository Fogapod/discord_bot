import discord

from pink.bot import PINK
from pink.cog import Cog
from pink.context import Context
from pink.settings import BaseSettings, settings


class CogSettings(BaseSettings):
    server: int
    user_log_channel: int
    all_role: int

    class Config(BaseSettings.Config):
        section = "cog.servermyserver"


cog_settings = settings.subsettings(CogSettings)


class ServerMyServer(Cog):
    """All logic related to ServerMyServer"""

    async def cog_check(self, ctx: Context) -> bool:
        return ctx.guild and ctx.guild.id == cog_settings.server

    async def _member_log(self, text: str) -> None:
        channel = self.bot.get_channel(cog_settings.user_log_channel)

        await channel.send(text)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await self._member_log(f"**{member}**[{member.id}] joined")

    @Cog.listener()
    async def on_member_leave(self, member: discord.Member) -> None:
        await self._member_log(f"**{member}**[{member.id}] left")


async def setup(bot: PINK) -> None:
    await bot.add_cog(ServerMyServer(bot))
