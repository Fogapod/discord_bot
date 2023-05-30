import inspect
import re
import time

from collections.abc import Callable, Iterable
from importlib import metadata
from pathlib import Path
from types import FunctionType, MethodDescriptorType, MethodType, ModuleType
from typing import Any, Optional, Type

import discord

from discord.ext import commands

from src.classes.bot import PINK, Prefix
from src.classes.cog import Cog
from src.classes.context import Context
from src.errors import PINKError
from src.settings import settings
from src.utils import seconds_to_human_readable

# art by: patorjk.com/software/taag
PINK_ART = r"""   ___ _____    __
  / _ \\_   \/\ \ \/\ /\
 / /_)/ / /\/  \/ / //_/
/ ___/\/ /_/ /\  / __ \
\/   \____/\_\ \/\/  \/"""

REPO = "git.based.computer/fogapod/pink"
SUPPORT = "TNXn8R7"
AUTHORS = (386551253532147712, 253384991940149249)

MAX_PREFIX_LEN = 256


class CustomHelp(commands.DefaultHelpCommand):
    def get_destination(self) -> Context:  # type: ignore[override]
        return self.context  # type: ignore[return-value]


class Meta(Cog):
    """Bot related utility commands"""

    async def cog_load(self) -> None:
        self.old_help_command = self.bot.help_command

        self.bot.help_command = CustomHelp()
        self.bot.help_command.cog = self

    async def cog_unload(self) -> None:
        self.bot.help_command = self.old_help_command

    @commands.command(aliases=["pink"])
    async def ping(self, ctx: Context) -> None:
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
            "source": f"{REPO} - {ctx.bot.version}",
            "support": f"discord.gg / {SUPPORT}",
            "owners": " ".join(owner_mentions),
            "uptime": seconds_to_human_readable(int(time.monotonic() - ctx.bot.launched_at)),
        }

        longest_filed = len(max(*list(fields.keys()), key=lambda s: len(s)))
        info = "\n".join(f"{k:>{longest_filed}} : {v}" for k, v in fields.items())

        await ctx.send(f"```\n{PINK_ART}\n\n{info}```")

    def _get_object_for_source_inspection(
        self, ctx: Context, name: str
    ) -> Iterable[Type[Any] | FunctionType | MethodType | MethodDescriptorType | Callable[..., Any] | ModuleType]:
        object_aliases = {
            "Bot": ctx.bot,
            "Context": ctx,
        }
        module_aliases = {
            "discord": discord,
        }

        if name.lower() == "help" or name.lower().startswith("help "):
            return [type(ctx.bot.help_command)]

        if (command := ctx.bot.get_command(name)) is not None:
            return [command.callback]

        if (cog := ctx.bot.get_cog(name)) is not None:
            return [type(cog)]

        if (obj := object_aliases.get(name)) is not None:
            return [type(obj)]

        if (obj := module_aliases.get(name)) is not None:
            return [obj]

        if name.startswith("on_"):
            if (events := ctx.bot.extra_events.get(name)) is not None:
                return events

            if (event := getattr(ctx.bot, name, None)) is not None:
                return [event]

            return ()

        # attribute source
        object_name, _, attr_chain_str = name.partition(".")
        if not attr_chain_str:
            return ()

        for getter in (
            object_aliases.get,
            module_aliases.get,
            ctx.bot.get_cog,
        ):
            if (obj := getter(object_name)) is not None:  # type: ignore[operator]
                break
        else:
            return ()

        attr_chain = attr_chain_str.split(".")

        for i, attr in enumerate(attr_chain):
            # only return properties when we are at final attr. otherwise use property value
            if i + 1 == len(attr_chain):
                if inspect.isclass(obj):
                    obj_class = obj
                else:
                    obj_class = type(obj)

                if isinstance(prop := getattr(obj_class, attr, None), property):
                    return filter(None, [prop.fget, prop.fset, prop.fdel])

            if (obj := getattr(obj, attr, None)) is None:
                # lookup failed
                return ()

            if isinstance(obj, commands.Command):
                obj = obj.callback
        if not (
            inspect.isfunction(obj)
            or inspect.ismethod(obj)
            or inspect.ismethoddescriptor(obj)
            or inspect.ismodule(obj)
            or inspect.isclass(obj)
        ):
            # we're at some attribute, try getting it's type
            obj = type(obj)

        return [obj]

    @staticmethod
    def _github_object_url(
        *,
        repo: str,
        branch: str,
        obj: Optional[
            Type[Any] | FunctionType | MethodType | MethodDescriptorType | Callable[..., Any] | ModuleType
        ] = None,
    ) -> str:
        base = f"https://{repo}"

        if obj is None:
            base += f"/tree/{branch}"
        else:
            lines, starting_line = inspect.getsourcelines(obj)

            if isinstance(obj, ModuleType):
                object_module = obj.__name__
                starting_line += 1
            else:
                object_module = obj.__module__

            file_path = Path(*object_module.split("."))

            if file_path.is_dir():
                file_path = file_path / "__init__.py"
            else:
                file_path = file_path.with_suffix(".py")

            base += f"/blob/{branch}/{'/'.join(file_path.parts)}#L{starting_line}-L{starting_line + len(lines) - 1}"

        return base

    @staticmethod
    def _gitea_object_url(
        *,
        repo: str,
        branch: Optional[str],
        commit: Optional[str],
        obj: Optional[
            Type[Any] | FunctionType | MethodType | MethodDescriptorType | Callable[..., Any] | ModuleType
        ] = None,
    ) -> str:
        base = f"https://{repo}"

        if commit is not None:
            base += f"/src/commit/{commit}"
        elif branch is not None:
            base += f"/src/branch/{branch}"
        else:
            raise ValueError("Expected commit or branch")

        if obj is not None:
            lines, starting_line = inspect.getsourcelines(obj)

            if isinstance(obj, ModuleType):
                object_module = obj.__name__
                starting_line += 1
            else:
                object_module = obj.__module__

            file_path = Path(*object_module.split("."))

            if file_path.is_dir():
                file_path = file_path / "__init__.py"
            else:
                file_path = file_path.with_suffix(".py")

            base += f"/{'/'.join(file_path.parts)}#L{starting_line}-L{starting_line + len(lines) - 1}"

        return base

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
            if isinstance(obj, ModuleType):
                object_module = thing
            else:
                object_module = obj.__module__

            object_top_level_module, *_ = object_module.partition(".")

            # show source for supported modules (only discord.py for now)
            if object_top_level_module == "discord":
                repo = "github.com/Rapptz/discord.py"

                dpy_version = metadata.version("discord.py")

                # dev versions have git commit, use it
                if git_sha_match := re.fullmatch(r".+?\+g(\w+)", dpy_version):
                    branch = git_sha_match[1]
                else:
                    # take only major and minor versions
                    dpy_semver = re.match(r"\d+\.\d+", dpy_version)[0]  # type: ignore
                    # dpy branch naming rules: v1.5.x
                    branch = f"v{dpy_semver}.x"

                url = self._github_object_url(
                    repo=repo,
                    branch=branch,
                    obj=None if thing == "discord" else obj,
                )
            else:
                top_level_module, *_ = self.__module__.partition(".")
                if top_level_module != object_top_level_module:
                    raise PINKError(f"`{thing}` is defined in external module: `{object_module}`")

                repo = REPO
                commit = None
                branch = None

                if (commit := ctx.bot.version.git_commit) is None:
                    if (branch := ctx.bot.version.git_branch) is None:
                        branch = "main"

                url = self._gitea_object_url(
                    repo=repo,
                    commit=commit,
                    branch=branch,
                    obj=obj,
                )

            result += f"`{object_module}`: <{url}>\n"

        if self.bot.version.is_dirty:
            result += "\nNOTE: running in dirty repository, location might be inaccurate"

        await ctx.send(result)

    @commands.group(
        invoke_without_command=True,
        ignore_extra=False,
    )
    @commands.guild_only()
    async def prefix(self, ctx: Context) -> None:
        """Get local prefix (if any)."""

        assert ctx.guild is not None

        if ctx.guild.id not in ctx.bot.prefixes:
            return await ctx.send(f"Custom prefix not set, default is @mention or {settings.bot.prefix}")

        await ctx.send(f"Local prefix: {ctx.bot.prefixes[ctx.guild.id].prefix}")

    @prefix.command()  # type: ignore
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx: Context, *, prefix: str) -> None:
        """
        Set custom prefix for server
        """

        assert ctx.guild is not None

        if len(prefix) > MAX_PREFIX_LEN:
            await ctx.reply(f"Max prefix len exceeded[{MAX_PREFIX_LEN}]: {prefix[:MAX_PREFIX_LEN]}")
            return

        settings = Prefix(ctx.bot, prefix=prefix.lower())
        await settings.write(ctx)

        ctx.bot.prefixes[ctx.guild.id] = settings

        await ctx.ok()

    @prefix.command(aliases=["remove", "del"])  # type: ignore
    @commands.has_permissions(manage_guild=True)
    async def unset(self, ctx: Context) -> None:
        """
        Remove local prefix override
        """

        assert ctx.guild is not None

        if ctx.guild.id in ctx.bot.prefixes:
            await Prefix.delete(ctx)

            del ctx.bot.prefixes[ctx.guild.id]

        await ctx.ok()


async def setup(bot: PINK) -> None:
    await bot.add_cog(Meta(bot))
