"""
This is heavily based on E accent.
"""

from __future__ import annotations

import random

from collections.abc import Generator
from math import log10
from typing import Any

from pink_accents import Accent, Match, Replacement, ReplacementContext
from pink_accents.errors import BadSeverityError


def excited(m: Match) -> str:
    state: State = m.context.state  # type: ignore[assignment]

    # special value
    if m.severity == 0:
        if state.previous_capital:
            fn = str.lower
        else:
            fn = str.upper

        m.context.state.previous_capital = not state.previous_capital  # type: ignore[union-attr]

        return fn(m.original)

    if m.severity < 0:
        fn = str.lower
    else:
        fn = str.upper

    if m.context.state.next_float() + log10(abs(m.severity)) > 0.5:  # type: ignore[union-attr]
        return fn(m.original)

    return m.original


class State:
    __slots__ = (
        "_generator",
        "previous_capital",
    )

    def __init__(self, ctx: ReplacementContext[State]):
        self._generator = self._float_generator(len(ctx.source))
        self.previous_capital = False

    def next_float(self) -> float:
        return next(self._generator)

    @staticmethod
    def _float_generator(count: int) -> Generator[float, None, None]:
        yield from [random.random() for _ in range(count)]


class Excited(Accent):
    """You feel excited"""

    REPLACEMENTS = [Replacement(r"[a-z]", excited, adjust_case=False)]  # noqa: RUF012

    # mypy does not understand properties at all
    @Accent.severity.setter  # type: ignore
    def severity(self, value: int) -> None:
        # support negative severity
        if not isinstance(value, int):
            raise BadSeverityError("Must be integer")

        self._severity = value

    # TODO: fix this argument mess in library
    def get_context(
        self,
        *,
        text: str,
        context_id: Any,
        # renaming to _cls or _ breaks mypy for some reason:
        # Signature of "get_context" incompatible with supertype "Accent"
        cls: type[ReplacementContext[State]] = ReplacementContext[State],  # noqa: ARG002
    ) -> ReplacementContext[State]:
        ctx: ReplacementContext[State] = ReplacementContext(
            source=text,
            id=context_id,
            accent=self,
        )
        ctx.state = State(ctx)

        return ctx
