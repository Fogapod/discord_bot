import io
import copy
import json
import random
import asyncio
import textwrap
import traceback

from typing import Any, Dict, Union, Iterator, Sequence
from contextlib import redirect_stdout

import discord

from discord.ext import commands

from potato_bot.bot import Bot
from potato_bot.cog import Cog
from potato_bot.utils import run_process_shell
from potato_bot.checks import is_owner
from potato_bot.context import Context


class TechAdmin(Cog):
    """Commands for technical staff"""

    SQL_VALUE_LEN_CAP = 30
    PAGINATOR_PAGES_CAP = 5

    async def cog_check(self, ctx: Context) -> None:
        return await is_owner().predicate(ctx)

    @commands.command()
    async def load(self, ctx: Context, module: str) -> None:
        """Load extension"""

        self.bot.load_extension(f"potato_bot.cogs.{module}")
        await ctx.ok()

    @commands.command()
    async def unload(self, ctx: Context, module: str) -> None:
        """Unload extension"""

        self.bot.unload_extension(f"potato_bot.cogs.{module}")
        await ctx.ok()

    @commands.command()
    async def reload(self, ctx: Context, module: str) -> None:
        """Reload extension"""

        self.bot.reload_extension(f"potato_bot.cogs.{module}")
        await ctx.ok()

    # https://github.com/Rapptz/RoboDanny/blob/715a5cf8545b94d61823f62db484be4fac1c95b1/cogs/admin.py#L422
    @commands.command(aliases=["sudo", "doas", "da"])
    async def runas(
        self, ctx: Context, user: Union[discord.Member, discord.User], *, command: str
    ) -> None:
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
        max_page_size = (
            paginator.max_size - len(paginator.prefix) - len(paginator.suffix) - 2
        )

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
                yield text[-line_len - 1 :]

        for line in wrap_with_limit(text, max_page_size):
            paginator.add_line(line)

        return paginator

    async def _send_paginator(
        self, ctx: Context, paginator: commands.Paginator
    ) -> None:
        if len(paginator.pages) > self.PAGINATOR_PAGES_CAP:
            pages = paginator.pages[-self.PAGINATOR_PAGES_CAP :]

            await ctx.send(
                f"Sending last **{len(pages)}** of **{len(paginator.pages)}** pages"
            )
        else:
            pages = paginator.pages

        for page in pages:
            await ctx.send(page)

    @commands.command()
    async def eval(self, ctx: Context, *, program: str) -> None:
        """
        Evaluate code inside bot, with async support
        Has conveniece shortcuts like
        - ctx
        - discord

        To get result you can either print or return object.
        """

        if program.startswith("```") and program.endswith("```"):
            # strip codeblock
            program = program[:-3]
            program = "\n".join(program.split("\n")[1:])

        async with ctx.typing():
            result = await self._eval(ctx, program)
            result = result.replace(self.bot.http.token, "TOKEN_LEAKED")

            paginator = self._make_paginator(result, prefix="```py\n")

            await self._send_paginator(ctx, paginator)

    @commands.command()
    async def exec(self, ctx: Context, *, arguments: str) -> None:
        """Execute shell command"""

        async with ctx.typing():
            paginator = await self._exec(ctx, arguments)

            await self._send_paginator(ctx, paginator)

    @commands.command(aliases=["edgeql", "edb"])
    async def edgedb(self, ctx: Context, *, program: str) -> None:
        """Run EdgeQL code against bot database"""

        async with ctx.typing():
            # https://github.com/edgedb/edgedb-python/issues/107
            data = json.loads(await ctx.edb.query_json(program))

            if not data:
                return await ctx.ok()

            paginator = await self._sql_table(data)

            await self._send_paginator(ctx, paginator)

    async def _eval(self, ctx: Context, program: str) -> str:
        # copied from https://github.com/Fogapod/KiwiBot/blob/49743118661abecaab86388cb94ff8a99f9011a8/modules/owner/module_eval.py
        # (originally copied from R. Danny bot)
        glob = {
            "self": self,
            "bot": self.bot,
            "ctx": ctx,
            "message": ctx.message,
            "guild": ctx.guild,
            "author": ctx.author,
            "channel": ctx.channel,
            "asyncio": asyncio,
            "random": random,
            "discord": discord,
        }

        fake_stdout = io.StringIO()

        to_compile = "async def func():\n" + textwrap.indent(program, "  ")

        try:
            exec(to_compile, glob)
        except Exception as e:
            return f"{e.__class__.__name__}: {e}"

        func = glob["func"]

        try:
            with redirect_stdout(fake_stdout):
                returned = await func()
        except asyncio.CancelledError:
            raise
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

    async def _exec(self, ctx: Context, arguments: str) -> commands.Paginator:
        stdout, stderr = await run_process_shell(arguments)

        if stderr:
            result = f"STDERR:\n{stderr}\n{stdout}"
        else:
            result = stdout

        result = result.replace(self.bot.http.token, "TOKEN_LEAKED")

        return self._make_paginator(result, prefix="```bash\n")

    async def _sql_table(
        self, result: Union[Sequence[Dict[str, Any]], Sequence[Any]]
    ) -> commands.Paginator:
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
                        self.SQL_VALUE_LEN_CAP,
                    )
                )

        header = " | ".join(
            f"{column:^{col_widths[i]}}" for i, column in enumerate(columns)
        )
        separator = "-+-".join("-" * width for width in col_widths)

        def sanitize_value(value: Any) -> str:
            value = str(value).replace("\n", "\\n")

            if len(value) > self.SQL_VALUE_LEN_CAP:
                value = f"{value[:self.SQL_VALUE_LEN_CAP - 2]}.."

            return value

        paginator = commands.Paginator(prefix="```python\n")
        paginator.add_line(header)
        paginator.add_line(separator)

        for row in result:
            paginator.add_line(
                " | ".join(
                    f"{sanitize_value(value):<{col_widths[i]}}"
                    for i, value in enumerate(row.values())
                )
            )

        return paginator


def setup(bot: Bot) -> None:
    bot.add_cog(TechAdmin(bot))
