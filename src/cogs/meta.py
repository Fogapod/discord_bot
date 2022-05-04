import inspect
import os
import time

from pathlib import Path
from types import FunctionType, MethodType
from typing import Any, Iterable, Optional, Type, Union

from discord.ext import commands  # type: ignore[attr-defined]

from src.bot import PINK, Prefix
from src.cog import Cog
from src.context import Context
from src.settings import settings
from src.utils import seconds_to_human_readable

# art by: patorjk.com/software/taag
PINK_ART = r"""   ___ _____    __
  / _ \\_   \/\ \ \/\ /\
 / /_)/ / /\/  \/ / //_/
/ ___/\/ /_/ /\  / __ \
\/   \____/\_\ \/\/  \/"""

REPO = "github.com/Fogapod/pink"
SUPPORT = "TNXn8R7"
AUTHORS = (386551253532147712, 253384991940149249)

MAX_PREFIX_LEN = 256


class CustomHelp(commands.DefaultHelpCommand):
    def get_destination(self) -> Context:
        return self.context


class Meta(Cog):
    """Bot related utility commands"""

    async def cog_load(self) -> None:
        self.old_help_command = self.bot.help_command

        self.bot.help_command = CustomHelp()
        self.bot.help_command.cog = self

    async def cog_unload(self) -> None:
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

        owner_mentions = []
        for owner_id in dict.fromkeys([*AUTHORS, *self.bot.owner_ids]).keys():
            if owner := await self.bot.maybe_get_user(owner_id):
                if owner.id in AUTHORS and owner.id not in self.bot.owner_ids:
                    owner_mentions.append(f"{owner}[inactive]")
                else:
                    # put active and resolved owners at the beginning
                    owner_mentions.insert(0, str(owner))
            else:
                owner_mentions.append(f"[{owner_id}]")

        fields = {
            "prefix": f"@mention or {settings.bot.prefix}",
            "source": f"{REPO} {revision}",
            "support": f"discord.gg / {SUPPORT}",
            "owners": " ".join(owner_mentions),
            "uptime": seconds_to_human_readable(int(time.monotonic() - ctx.bot.launched_at)),
        }

        longest_filed = len(max(*list(fields.keys()), key=lambda s: len(s)))
        info = "\n".join(f"{k:>{longest_filed}} : {v}" for k, v in fields.items())

        await ctx.send(f"```\n{PINK_ART}\n\n{info}```")

    def _get_object_for_source_inspection(
        self, ctx: Context, name: str
    ) -> Iterable[Union[Type[Any], FunctionType, MethodType]]:
        if name == "help":
            return [type(ctx.bot.help_command)]

        if (command := ctx.bot.get_command(name)) is not None:
            return [command.callback]

        if (cog := ctx.bot.get_cog(name)) is not None:
            return [type(cog)]

        if name.startswith("on_"):
            if (events := ctx.bot.extra_events.get(name)) is not None:
                return events

            if (event := getattr(ctx.bot, name, None)) is not None:
                return [event]

            return ()

        object_aliases = {
            "Bot": PINK,
            "Context": Context,
        }

        object_name, _, method = name.partition(".")
        if not method:
            return ()

        if (obj := object_aliases.get(object_name)) is None:
            if (obj := ctx.bot.get_cog(object_name)) is None:
                return ()

        if (attr := getattr(obj, method, None)) is not None:
            if isinstance(attr, commands.Command):
                return [attr.callback]

            if inspect.isroutine(attr):
                # this can theoretically be some sort of callable from other library. we want none of that
                top_level_module, _ = self.__module__.split(".", 1)
                if attr.__module__.startswith(f"{top_level_module}."):
                    return [attr]  # type: ignore

        return ()

    @commands.command(aliases=["src"])
    async def source(self, ctx: Context, *, thing: Optional[str]) -> None:
        """
        Get source code of command, module, event or bot

        Use on_ prefix for events.

        Some objects allow method lookup using dot (Bot.get_prefix):
          - Bot
          - Context
          - Any valid cog
        """

        if thing is None:
            await ctx.send(f"<https://{REPO}>")
            return

        if not (objs := self._get_object_for_source_inspection(ctx, thing)):
            await ctx.reply("Command, cog or event not found")
            return

        result = ""

        for obj in objs:
            lines, starting_line = inspect.getsourcelines(obj)

            file_path = Path(*obj.__module__.split("."))
            if file_path.is_dir():
                file_path = file_path / "__init__.py"
            else:
                file_path = file_path.with_suffix(".py")

            # try commit, fallback to branch, fallback to "main" branch
            branch = os.environ.get("GIT_COMMIT", os.environ.get("GIT_BRANCH", "main"))

            # github specific layout
            result += f"`{obj.__module__}`: <https://{REPO}/blob/{branch}/{file_path}#L{starting_line}-L{starting_line + len(lines) - 1}>\n"

        if os.environ.get("GIT_DIRTY", "0") != "0":
            result += "\nNOTE: running in dirty repository, location might be inaccurate"

        await ctx.send(result)

    @commands.group(
        invoke_without_command=True,
        ignore_extra=False,
    )
    @commands.guild_only()
    async def prefix(self, ctx: Context) -> None:
        """Get local prefix (if any)."""

        if ctx.guild.id not in ctx.bot.prefixes:
            return await ctx.send(f"Custom prefix not set, default is @mention or {settings.bot.prefix}")

        await ctx.send(f"Local prefix: {ctx.bot.prefixes[ctx.guild.id].prefix}")

    @prefix.command()
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx: Context, *, prefix: str) -> None:
        """
        Set custom prefix for server
        """

        if len(prefix) > MAX_PREFIX_LEN:
            await ctx.reply(f"Max prefix len exceeded[{MAX_PREFIX_LEN}]: {prefix[:MAX_PREFIX_LEN]}")
            return

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


async def setup(bot: PINK) -> None:
    await bot.add_cog(Meta(bot))
