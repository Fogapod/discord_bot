"""
This is heavily based on E accent.
"""

import random

from math import log10
from typing import Any, Type, Generator

from pink_accents import Match, Accent, Replacement, ReplacementContext
from pink_accents.errors import BadSeverity


def excited(m: Match) -> str:
    # special value
    if m.severity == 0:
        if m.context.state.previous_capital:
            fn = str.lower
        else:
            fn = str.upper

        m.context.state.previous_capital = not m.context.state.previous_capital

        return fn(m.original)

    if m.severity < 0:
        fn = str.lower
    else:
        fn = str.upper

    if m.context.state.next_float() + log10(abs(m.severity)) > 0.5:
        return fn(m.original)

    return m.original


class State:
    __slots__ = (
        "_generator",
        "previous_capital",
    )

    def __init__(self, ctx: ReplacementContext):
        self._generator = self._float_generator(len(ctx.source))
        self.previous_capital = False

    def next_float(self) -> float:
        return next(self._generator)

    @staticmethod
    def _float_generator(count: int) -> Generator[float, None, None]:
        yield from [random.random() for _ in range(count)]


class Excited(Accent):
    """You feel excited"""

    REPLACEMENTS = [Replacement(r"[a-z]", excited, adjust_case=False)]

    # mypy does not understand properties at all
    @Accent.severity.setter  # type: ignore
    def severity(self, value: int) -> None:
        # support negative severity
        if not isinstance(value, int):
            raise BadSeverity("Must be integer")

        self._severity = value

    # TODO: fix this argument mess in library
    def get_context(
        self,
        *,
        text: str,
        context_id: Any,
        # renaming to _cls or _ breaks mypy for some reason:
        # Signature of "get_context" incompatible with supertype "Accent"
        cls: Type[ReplacementContext] = ReplacementContext,  # noqa: U100
    ) -> ReplacementContext:
        ctx = ReplacementContext(
            source=text,
            id=context_id,
            accent=self,
        )
        ctx.state = State(ctx)

        return ctx
