from __future__ import annotations

import ast
import asyncio
import copy
import io
import random
import re
import textwrap
import traceback

from contextlib import redirect_stdout
from typing import Any, Iterator, Optional, Union

import asyncpg
import discord

from discord.ext import commands  # type: ignore[attr-defined]

from src.bot import PINK
from src.checks import is_owner
from src.cog import Cog
from src.context import Context
from src.utils import run_process_shell


class Code:
    # i have no idea why + and - are allowed as language name
    _codeblock_regex = re.compile(r"```(?P<language>[\w+-]*)\n*(?P<body>.*?)\n*```[^`]*", re.DOTALL)

    __slots__ = (
        "language",
        "body",
        "has_codeblock",
    )

    def __init__(self, *, language: Optional[str], body: str, has_codeblock: bool = True):
        self.language = language
        self.body = body
        self.has_codeblock = has_codeblock

    @classmethod
    async def convert(cls, _: Context, argument: str) -> Code:
        if match := cls._codeblock_regex.fullmatch(argument):
            if body := match["body"]:
                language = match["language"] or None
            else:
                # discord displays language in codeblocks without code as code, be consistent with that
                language = None
                body = match["language"]

            return Code(language=language, body=body)

        return Code(language=None, body=argument, has_codeblock=False)

    def __str__(self) -> str:
        if not self.has_codeblock:
            return self.body

        # this is not completely accurate because it always inserts \n between language and body. also newlines around body are stripped
        return f"```{'' if self.language is None else self.language}\n{self.body}```"


class TechAdmin(Cog):
    """Commands for bot administrators"""

    PAGINATOR_PAGES_CAP = 5

    async def cog_check(self, ctx: Context) -> None:
        return await is_owner().predicate(ctx)  # type: ignore[attr-defined]

    async def cog_load(self) -> None:
        # this is not ideal because if TechAdmin itself is reloaded, this value is lost
        self._last_reloaded_module: Optional[str] = None

    @commands.command()
    async def load(self, ctx: Context, module: str) -> None:
        """Load extension"""

        await self.bot.load_extension(f"src.cogs.{module}")
        await ctx.ok()

    @commands.command()
    async def unload(self, ctx: Context, module: str) -> None:
        """Unload extension"""

        await self.bot.unload_extension(f"src.cogs.{module}")
        await ctx.ok()

    @commands.command(aliases=["re"])
    async def reload(self, ctx: Context, module: str) -> None:
        """Reload extension"""

        if module == "~":
            if self._last_reloaded_module is None:
                return await ctx.send("No previous reloaded module")

            module = self._last_reloaded_module
        else:
            self._last_reloaded_module = module

        await self.bot.reload_extension(f"src.cogs.{module}")

        # try deleting message for easier testing with frequent reloads
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.ok()

    # https://github.com/Rapptz/RoboDanny/blob/715a5cf8545b94d61823f62db484be4fac1c95b1/cogs/admin.py#L422
    @commands.command(aliases=["doas", "da"])
    async def runas(self, ctx: Context, user: Union[discord.Member, discord.User], *, command: str) -> None:
        """Run command as other user"""

        msg = copy.copy(ctx.message)
        msg.channel = ctx.channel
        msg.author = user
        msg.content = f"{ctx.prefix}{command}"
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))

        await self.bot.invoke(new_ctx)
        await ctx.ok()

    def _make_paginator(self, text: str, prefix: str = "```") -> commands.Paginator:
        paginator = commands.Paginator(prefix=prefix)
        # https://github.com/Rapptz/discord.py/blob/5c868ed871184b26a46319c45a799c190e635892/discord/ext/commands/help.py#L125
        max_page_size = paginator.max_size - len(paginator.prefix) - len(paginator.suffix) - 2

        def wrap_with_limit(text: str, limit: int) -> Iterator[str]:
            limit -= 1

            line_len = 0

            for i, c in enumerate(text):
                if c == "\n" or line_len > limit:
                    yield text[i - line_len : i]

                    line_len = 0
                else:
                    line_len += 1

            if line_len != 0:
                yield text[-line_len:]

        for line in wrap_with_limit(text, max_page_size):
            paginator.add_line(line)

        return paginator

    async def _send_paginator(self, ctx: Context, paginator: commands.Paginator) -> None:
        if len(paginator.pages) > self.PAGINATOR_PAGES_CAP:
            pages = paginator.pages[-self.PAGINATOR_PAGES_CAP :]

            await ctx.send(f"Sending last **{len(pages)}** of **{len(paginator.pages)}** pages")
        else:
            pages = paginator.pages

        for page in pages:
            await ctx.send(page)

    @commands.command()
    async def eval(self, ctx: Context, *, code: Code) -> None:
        """
        Evaluate code inside bot, with async support
        Has conveniece shortcuts like
        - ctx
        - discord
        """

        async with ctx.typing():
            result = await self._eval(ctx, code)
            result = result.replace(self.bot.http.token, "TOKEN_LEAKED")

            paginator = self._make_paginator(result, prefix="```py\n")

        await self._send_paginator(ctx, paginator)

    @commands.command()
    async def exec(self, ctx: Context, *, code: Code) -> None:
        """Execute shell command"""

        async with ctx.typing():
            paginator = await self._exec(ctx, code.body)

        await self._send_paginator(ctx, paginator)

    @commands.command(aliases=["select"])
    async def sql(self, ctx: Context, *, code: Code) -> None:
        """Run SQL code against bot database"""

        # same parameters as eval
        query = code.body.format(ctx=ctx, message=ctx.message, guild=ctx.guild, author=ctx.author, channel=ctx.channel)

        if ctx.invoked_with == "select":
            query = f"SELECT {query}"

        async with ctx.typing():
            try:
                data = await ctx.pg.fetch(query)
            except asyncpg.PostgresError as e:
                return await ctx.send(f"Error: **{type(e).__name__}**: `{e}`")

            if not data:
                await ctx.ok()
                return

            paginator = await self._sql_table(data)

        await self._send_paginator(ctx, paginator)

    async def _eval(self, ctx: Context, code: Code) -> str:
        # copied from https://github.com/Fogapod/KiwiBot/blob/49743118661abecaab86388cb94ff8a99f9011a8/modules/owner/module_eval.py
        # (originally copied from R. Danny bot)
        glob = {
            "bot": self.bot,
            "ctx": ctx,
            "message": ctx.message,
            "guild": ctx.guild,
            "author": ctx.author,
            "channel": ctx.channel,
            "asyncio": asyncio,
            "discord": discord,
            "random": random,
        }

        # insert return
        code_no_last_line, maybe_nl, code_last_line = code.body.rpartition("\n")
        if not code_last_line.startswith(("return ", "raise ")):
            # special syntax for not inserting final return
            if code_last_line.startswith("!"):
                code_last_line = code_last_line[1:]
            else:
                # ignore code that is already invalid. this may also fail if there is a multiline expression since we
                # only take last line, we do not want to put return there either
                if self._is_valid_syntax(code_last_line):
                    code_last_line_with_return = f"return {code_last_line}"
                    # may fail if this is assignment and probably some other cases
                    if self._is_valid_syntax(code_last_line_with_return):
                        code_last_line = code_last_line_with_return

        indented_source = textwrap.indent(f"{code_no_last_line}{maybe_nl}{code_last_line}", "    ")
        wrapped_source = f"""\
async def __pink_eval__():
{indented_source}\
"""

        # NOTE: docs exclicitly say exception value can be passed to format_exception_only since 3.10
        try:
            exec(wrapped_source, glob)
        except Exception as e:
            return "".join(traceback.format_exception_only(e))  # type: ignore[arg-type]

        fake_stdout = io.StringIO()

        try:
            with redirect_stdout(fake_stdout):
                returned = await glob["__pink_eval__"]()
        except Exception as e:
            return f"{fake_stdout.getvalue()}{''.join(traceback.format_exception_only(e))}"  # type: ignore[arg-type]

        from_stdout = fake_stdout.getvalue()

        if returned is None:
            if from_stdout:
                return from_stdout

            return "Evaluated"

        return f"{from_stdout}{returned}"

    @staticmethod
    def _is_valid_syntax(source: str) -> bool:
        try:
            ast.parse(source)
        except SyntaxError:
            return False

        return True

    async def _exec(self, _: Context, arguments: str) -> commands.Paginator:
        stdout, stderr = await run_process_shell(arguments)

        if stderr:
            result = f"STDERR:\n{stderr}\n{stdout}"
        else:
            result = stdout

        result = result.replace(self.bot.http.token, "TOKEN_LEAKED")

        return self._make_paginator(result, prefix="```bash\n")

    async def _sql_table(self, result: list[asyncpg.Record]) -> commands.Paginator:
        # convert to list because otherwise iterator is exhausted
        columns = list(result[0].keys())
        col_widths = [len(c) for c in columns]

        for row in result:
            for i, value in enumerate(row.values()):
                col_widths[i] = max((col_widths[i], len(str(value))))

        header = " | ".join(f"{column:^{col_widths[i]}}" for i, column in enumerate(columns))
        separator = "-+-".join("-" * width for width in col_widths)

        def sanitize_value(value: Any) -> str:
            return str(value).replace("\n", "\\n")

        paginator = commands.Paginator(prefix="```sql\n")
        paginator.add_line(header)
        paginator.add_line(separator)

        for row in result:
            paginator.add_line(
                " | ".join(f"{sanitize_value(value):<{col_widths[i]}}" for i, value in enumerate(row.values()))
            )

        return paginator


async def setup(bot: PINK) -> None:
    await bot.add_cog(TechAdmin(bot))
