import discord

from discord.ext import commands

from pink.bot import PINK
from pink.cog import Cog
from pink.context import Context
from pink.settings import BaseSettings, settings


class NotServerMyServer(commands.CommandError):
    def __init__(self) -> None:
        super().__init__("Not ServerMyServer")


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
        if not (ctx.guild and ctx.guild.id == cog_settings.server):
            raise NotServerMyServer

        return True

    async def _member_log(self, text: str) -> None:
        channel: discord.TextChannel = self.bot.get_channel(cog_settings.user_log_channel)  # type: ignore

        await channel.send(text)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.guild.id != cog_settings.server:
            return

        await self._member_log(f"**{member}**[{member.id}] joined")

    @Cog.listener()
    async def on_member_leave(self, member: discord.Member) -> None:
        if member.guild.id != cog_settings.server:
            return

        await self._member_log(f"**{member}**[{member.id}] left")

    @commands.command(name="all")
    async def all_(self, ctx: Context) -> None:
        """Toggles @all role for you"""

        all_role: discord.Role = ctx.guild.get_role(self.settings.all_role)  # type: ignore
        reason = "asked"

        if ctx.author.get_role(all_role.id) is None:  # type: ignore
            await ctx.author.add_roles(all_role, reason=reason)  # type: ignore
        else:
            await ctx.author.remove_roles(all_role, reason=reason)  # type: ignore

        await ctx.ok()


async def setup(bot: PINK) -> None:
    await bot.add_cog(ServerMyServer(bot))
