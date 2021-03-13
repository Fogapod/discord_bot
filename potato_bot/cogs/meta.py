from time import perf_counter
from typing import Any

from discord.ext import commands

from potato_bot.bot import Bot, Prefix
from potato_bot.cog import Cog
from potato_bot.context import Context
from potato_bot.constants import PREFIX

POTATO_ART = r"""   ___      _        _
  / _ \___ | |_ __ _| |_ ___
 / /_)/ _ \| __/ _` | __/ _ \
/ ___/ (_) | || (_| | || (_) |
\/    \___/ \__\__,_|\__\___/"""


class CustomHelp(commands.DefaultHelpCommand):
    def get_destination(self) -> Context:
        return self.context


class Meta(Cog):
    """Bot related utility commands"""

    def __init__(self, bot: Bot):
        super().__init__(bot)

        self.old_help_command = bot.help_command

        bot.help_command = CustomHelp()
        bot.help_command.cog = self

    def cog_unload(self) -> None:
        self.bot.help_command = self.old_help_command

    @commands.command(aliases=["p"])
    async def ping(self, ctx: Context, *args: Any) -> None:
        """Check bot latency"""

        start = perf_counter()
        m = await ctx.send("pinging")
        send_diff = round((perf_counter() - start) * 1000)

        latency = round(self.bot.latency * 1000)

        await ctx.edit(
            m, content=f"Pong, **{send_diff}ms**\n\nLatency: **{latency}ms**"
        )

    @commands.command(aliases=["info"])
    async def about(self, ctx: Context) -> None:
        """General information about bot"""

        owners = [await self.bot.fetch_user(oid) for oid in self.bot.owner_ids]

        authors = f"Author{'s' if len(owners) > 1 else ''}: {', '.join(str(o) for o in owners)}"
        invite = "TNXn8R7"

        return await ctx.send(
            f"```\n"
            f"{POTATO_ART}\n"
            f"\n"
            f"Potato art by: patorjk.com/software/taag\n"
            f"\n"
            f"This bot was originally made for PotatoStation server for UnityStation.\n"
            f"\n"
            f"Prefix: @mention or {PREFIX}\n"
            f"Source code: github.com/Fogapod/potato_bot\n"
            f"{authors}\n"
            f"Support server: discord.gg/{invite}\n"
            f"```"
        )

    @commands.group()
    @commands.guild_only()
    async def prefix(self, ctx: Context) -> None:
        """
        Get local prefix (if any)
        """

        if ctx.subcommand_passed:
            if ctx.invoked_subcommand:
                return
            else:
                return await ctx.send_help(ctx.command)

        if ctx.guild.id not in ctx.bot.prefixes:
            return await ctx.send(
                f"Custom prefix not set, default is @mention or {PREFIX}"
            )

        await ctx.send(f"Local prefix: {ctx.bot.prefixes[ctx.guild.id].prefix}")

    @prefix.command()
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx: Context, *, prefix: str) -> None:
        """
        Set custom prefix for server
        """

        settings = Prefix(ctx.bot, prefix=prefix.lower())
        await settings.write(ctx)

        ctx.bot.prefixes[ctx.guild.id] = settings

        await ctx.ok()

    @prefix.command(aliases=["remove", "del"])
    @commands.has_permissions(manage_guild=True)
    async def unset(self, ctx: Context) -> None:
        """
        Remove local prefix override
        """

        if ctx.guild.id in ctx.bot.prefixes:
            await Prefix.delete(ctx)

            del ctx.bot.prefixes[ctx.guild.id]

        await ctx.ok()


def setup(bot: Bot) -> None:
    bot.add_cog(Meta(bot))
