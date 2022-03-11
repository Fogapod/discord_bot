import os
import time

from discord.ext import commands  # type: ignore[attr-defined]

from pink.bot import PINK, Prefix
from pink.cog import Cog
from pink.constants import PREFIX
from pink.context import Context
from pink.utils import seconds_to_human_readable

PINK_ART = r"""   ___ _____    __
  / _ \\_   \/\ \ \/\ /\
 / /_)/ / /\/  \/ / //_/
/ ___/\/ /_/ /\  / __ \
\/   \____/\_\ \/\/  \/"""


class CustomHelp(commands.DefaultHelpCommand):
    def get_destination(self) -> Context:
        return self.context


class Meta(Cog):
    """Bot related utility commands"""

    def __init__(self, bot: PINK):
        super().__init__(bot)

        self.old_help_command = bot.help_command

        bot.help_command = CustomHelp()
        bot.help_command.cog = self

    def cog_unload(self) -> None:
        self.bot.help_command = self.old_help_command

    @commands.command(aliases=["pink"])
    async def ping(self, ctx: Context, *_args: str) -> None:
        """Check bot latency"""

        g_or_k = "g" if ctx.invoked_with == "ping" else "k"

        start = time.perf_counter()
        m = await ctx.send(f"pin{g_or_k}ing...")
        send_diff = round((time.perf_counter() - start) * 1000)

        latency = round(self.bot.latency * 1000)

        await ctx.edit(m, content=f"Pon{g_or_k}! Took **{send_diff}ms** to edit\n\nWS latency: **{latency}ms**")

    @commands.command(aliases=["info"])
    async def about(self, ctx: Context) -> None:
        """General information about bot"""

        if git_commit := os.environ.get("GIT_COMMIT"):
            revision = git_commit[:10]
            if git_branch := os.environ.get("GIT_BRANCH"):
                revision = f"{git_branch}/{revision}"

            if (git_dirty_files := os.environ.get("GIT_DIRTY", "0")) != "0":
                revision = f"{revision} DIRTY[{git_dirty_files}]"

            revision = f"[{revision}]"
        else:
            revision = ""

        owners = [await self.bot.fetch_user(oid) for oid in self.bot.owner_ids]
        authors = f"Author{'s' if len(owners) > 1 else ''}: {', '.join(str(o) for o in owners)}"

        invite = "TNXn8R7"

        running_for = seconds_to_human_readable(int(time.monotonic() - ctx.bot.launched_at))

        return await ctx.send(
            f"""```
{PINK_ART}

[PINK art by: patorjk.com/software/taag]

This bot was originally made for PotatoStation server of UnityStation.

Prefix: @mention or {PREFIX}
Source code: github.com/Fogapod/pink {revision}
{authors}
Support server: discord.gg / {invite}

Uptime: {running_for}
```"""
        )

    @commands.group(
        invoke_without_command=True,
        ignore_extra=False,
    )
    @commands.guild_only()
    async def prefix(self, ctx: Context) -> None:
        """Get local prefix (if any)."""

        if ctx.guild.id not in ctx.bot.prefixes:
            return await ctx.send(f"Custom prefix not set, default is @mention or {PREFIX}")

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


def setup(bot: PINK) -> None:
    bot.add_cog(Meta(bot))
