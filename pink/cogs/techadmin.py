from __future__ import annotations

import asyncio
import copy
import io
import random
import re
import textwrap
import traceback

from contextlib import redirect_stdout
from typing import Any, Dict, Iterator, Optional, Sequence, Union

import discord
import edgedb
import orjson

from discord.ext import commands  # type: ignore[attr-defined]

from pink.bot import PINK
from pink.checks import is_owner
from pink.cog import Cog
from pink.context import Context
from pink.utils import run_process_shell


class Code:
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
        # i have no idea why + and - are allowed as language name
        if match := re.match(r"```(?P<language>[\w+-]*)\n?(?P<body>.*?)```", argument):
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

        # this is not completely accurate because it always inserts \n between language and body
        return f"```{'' if self.language is None else self.language}\n{self.body}```"


class TechAdmin(Cog):
    """Commands for bot administrators"""

    EDB_VALUE_LEN_CAP = 30
    PAGINATOR_PAGES_CAP = 5

    async def cog_check(self, ctx: Context) -> None:
        return await is_owner().predicate(ctx)  # type: ignore[attr-defined]

    @commands.command()
    async def load(self, ctx: Context, module: str) -> None:
        """Load extension"""

        self.bot.load_extension(f"pink.cogs.{module}")
        await ctx.ok()

    @commands.command()
    async def unload(self, ctx: Context, module: str) -> None:
        """Unload extension"""

        self.bot.unload_extension(f"pink.cogs.{module}")
        await ctx.ok()

    @commands.command()
    async def reload(self, ctx: Context, module: str) -> None:
        """Reload extension"""

        self.bot.reload_extension(f"pink.cogs.{module}")
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

    @commands.command(aliases=["edgeql", "edb"])
    async def edgedb(self, ctx: Context, *, code: Code) -> None:
        """Run EdgeQL code against bot database"""

        async with ctx.typing():
            try:
                # https://github.com/edgedb/edgedb-python/issues/107
                data = orjson.loads(await ctx.edb.query_json(code.body))  # type: ignore[no-untyped-call]
            except edgedb.EdgeDBError as e:
                return await ctx.send(f"Error: **{type(e).__name__}**: `{e}`")

            if not data:
                await ctx.ok()
                return

            paginator = await self._edgedb_table(data)

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
        code_no_last_line, _, code_last_line = code.body.rpartition("\n")
        if not code_last_line.startswith(("return ", "raise ")):
            # special syntax for not inserting final return
            if code_last_line.startswith("!"):
                code_last_line = code_last_line[1:]
            else:
                code_last_line = f"return {code_last_line}"

        to_compile = "async def func():\n" + textwrap.indent(f"{code_no_last_line}\n{code_last_line}", "  ")

        try:
            exec(to_compile, glob)
        except Exception as e:
            return f"{type(e).__name__}: {e}"

        func = glob["func"]

        fake_stdout = io.StringIO()

        try:
            with redirect_stdout(fake_stdout):
                returned = await func()
        except Exception:
            return f"{fake_stdout.getvalue()}{traceback.format_exc()}"
        else:
            from_stdout = fake_stdout.getvalue()

            if returned is None:
                if from_stdout:
                    return f"{from_stdout}"

                return "Evaluated"
            else:
                return f"{from_stdout}{returned}"

    async def _exec(self, _: Context, arguments: str) -> commands.Paginator:
        stdout, stderr = await run_process_shell(arguments)

        if stderr:
            result = f"STDERR:\n{stderr}\n{stdout}"
        else:
            result = stdout

        result = result.replace(self.bot.http.token, "TOKEN_LEAKED")

        return self._make_paginator(result, prefix="```bash\n")

    async def _edgedb_table(self, result: Union[Sequence[Dict[str, Any]], Sequence[Any]]) -> commands.Paginator:
        if not isinstance(result[0], dict):
            paginator = commands.Paginator(prefix="```python\n")
            paginator.add_line(str(result))
            return paginator

        columns = result[0].keys()
        col_widths = [len(c) for c in columns]

        for row in result:
            for i, column in enumerate(columns):
                col_widths[i] = min(
                    (
                        max((col_widths[i], len(str(row[column])))),
                        self.EDB_VALUE_LEN_CAP,
                    )
                )

        header = " | ".join(f"{column:^{col_widths[i]}}" for i, column in enumerate(columns))
        separator = "-+-".join("-" * width for width in col_widths)

        def sanitize_value(value: Any) -> str:
            value = str(value).replace("\n", "\\n")

            if len(value) > self.EDB_VALUE_LEN_CAP:
                value = f"{value[:self.EDB_VALUE_LEN_CAP - 2]}.."

            return value

        paginator = commands.Paginator(prefix="```python\n")
        paginator.add_line(header)
        paginator.add_line(separator)

        for row in result:
            paginator.add_line(
                " | ".join(f"{sanitize_value(value):<{col_widths[i]}}" for i, value in enumerate(row.values()))
            )

        return paginator


def setup(bot: PINK) -> None:
    bot.add_cog(TechAdmin(bot))
