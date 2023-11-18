from __future__ import annotations

import re

from typing import Optional

from src.context import Context

__all__ = ("Code",)


class Code:
    _codeblock_regex = re.compile(r"```(?P<language>[\w+-]*)\n*(?P<body>.*?)\n*```\s*(?P<the_rest>[^`]*)", re.DOTALL)

    __slots__ = (
        "language",
        "body",
        "the_rest",
        "has_codeblock",
    )

    def __init__(self, *, language: Optional[str], body: str, the_rest: str, has_codeblock: bool = True):
        self.language = language
        self.body = body
        self.the_rest = the_rest
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

            return Code(language=language, body=body, the_rest=match["the_rest"])

        return Code(language=None, body=argument, the_rest="", has_codeblock=False)

    def __str__(self) -> str:
        if not self.has_codeblock:
            return self.body

        # this is not completely accurate because it always inserts \n between language and body. also newlines around
        # body are stripped
        return f"```{'' if self.language is None else self.language}\n{self.body}```"
