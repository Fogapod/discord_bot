from __future__ import annotations

import re
import math
import random
import itertools

from typing import Any, Dict, Tuple, Union, Callable, Optional, Sequence


class ReplacementContext:
    """
    Instance of this class is passed to every handler function as a part of Match.

    `id` is an arbitrary identificator of translation source. For example, user id.
    Passed value depends on implementation and might be not set at all (None).

    `state` can be used to store arbitrary accent state. Since every accent get their
    own instance of this context, accent is free to store any information there.
    """

    __slots__ = (
        "id",
        "state",
    )

    def __init__(self, id: Any = None):
        self.id = id
        self.state: Any = None

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id} state={self.state}>"


class Match:
    """
    Contains information about current match. Passed to every handler function.
    """

    __slots__ = (
        "match",
        "severity",
        "context",
    )

    def __init__(
        self, *, match: re.Match[str], severity: int, context: ReplacementContext
    ) -> None:
        self.match = match
        self.severity = severity
        self.context = context

    @property
    def original(self) -> str:
        """Original text that is being replaced"""

        return self.match[0]

    # !!!these ,ethods are a bunch of broken nonsense!!!
    def count_linear(self) -> int:
        return self.severity

    def count_logarithmic(self, base: int = 10) -> float:
        return min(
            (
                max((0.1, math.log(self.severity, base))),
                0.99,
            )
        )

    def count_exponential(self, base: int = 10) -> float:
        return 1 / (1 - self.count_logarithmic(base))

    def probability_linear(self, max_severity: int = 10) -> bool:
        return random.random() < self.severity / max_severity

    def probability_logarithmic(self, base: int = 10) -> bool:
        return random.random() < self.count_logarithmic(base)

    def probability_exponential(self, base: int = 10) -> bool:
        return random.random() < self.count_exponential(base)

    # !!!these ,ethods are a bunch of broken nonsense!!!

    def __repr__(self) -> str:
        return f"<{type(self).__name__} match={self.match} severity={self.severity} context={self.context}>"


_ReplacedType = Optional[str]
_ReplacementCallableType = Callable[[Match], _ReplacedType]
_ReplacementSequenceType = Sequence[Union[_ReplacedType, _ReplacementCallableType]]
_ReplacementDictType = Dict[
    Union[_ReplacedType, _ReplacementCallableType, _ReplacementSequenceType],
    int,
]
_ReplacementType = Union[
    str,
    _ReplacementSequenceType,
    _ReplacementDictType,
]


class Replacement:
    __slots__ = (
        "pattern",
        "callback",
    )

    def __init__(
        self,
        pattern: Union[str, re.Pattern[str]],
        replacement: _ReplacementType,
        flags: Any = re.IGNORECASE,
    ):
        if isinstance(pattern, re.Pattern):
            self.pattern = pattern
        else:
            self.pattern = re.compile(pattern, flags)

        self.callback = self._get_callback(replacement)

    @staticmethod
    def _get_callback(replacement: _ReplacementType) -> _ReplacementCallableType:
        if isinstance(replacement, str):

            def callback_static(match: Match) -> str:
                return replacement  # type: ignore

            return callback_static

        elif isinstance(replacement, Sequence):
            # sequence of equally weighted items
            def callback_select_equal(match: Match) -> _ReplacedType:
                selected = random.choice(replacement)  # type: ignore

                if isinstance(selected, str) or selected is None:
                    return selected

                return selected(match)

            return callback_select_equal

        elif isinstance(replacement, dict):
            # dict of weighted items
            keys = [*replacement.keys()]
            values = [*replacement.values()]

            computable_weights: Sequence[Tuple[int, Callable[[int], float]]] = []
            for i, v in enumerate(values):
                if not isinstance(v, (int, float)):
                    # assume is a callable
                    # TODO: proper check
                    computable_weights.append((i, v))

                    # compute for severity 1, fail early for ease of debugging
                    # also cleans values list from functions
                    values[i] = v(1)

            if not computable_weights:
                # inject None if total weight is < 1 for convenience
                # example: {"a": 0.25, "b": 0.5} -> {"a": 0.25, "b": 0.5, None: 0.25}
                if (values_sum := sum(values)) < 1:
                    keys.append(None)
                    values.append(1 - values_sum)

            # is only useful when there are no computable weights
            # computed as early optimization
            # https://docs.python.org/3/library/random.html#random.choices
            cum_weights = list(itertools.accumulate(values))

            def callback_select_weighted(match: Match) -> _ReplacedType:
                if computable_weights:
                    for index, fn in computable_weights:
                        # NOTE: is this racy? without threads it's fine I guess
                        # why is mypy angry???
                        values[index] = fn(match.severity)  # type: ignore

                    selected = random.choices(keys, weights=values)[0]
                else:
                    selected = random.choices(keys, cum_weights=cum_weights)[0]

                if isinstance(selected, str) or selected is None:
                    return selected

                return selected(match)  # type: ignore

            return callback_select_weighted
        else:
            # assume callable
            # TODO: check
            return replacement  # type: ignore

    def apply(
        self, text: str, *, severity: int, limit: int, context: ReplacementContext
    ) -> str:
        result_len = len(text)

        def repl(match: re.Match[str]) -> str:
            nonlocal result_len

            original = match[0]

            replacement = self.callback(
                Match(match=match, severity=severity, context=context)
            )
            if replacement is None:
                return original

            result_len += len(replacement) - len(original)
            if result_len > limit:
                return original

            if original.islower():
                return replacement

            if original.istitle():
                if replacement.islower():
                    # if there are some case variations better leave string untouched
                    return replacement.title()

            elif original.isupper():
                return replacement.upper()

            return replacement

        return self.pattern.sub(repl, text)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.pattern} => {self.callback}>"


class Accent:
    """
    Main accent class.

    Each time this class is inherited, child class is added to the pool of accents.

    Accent replacements are defined with WORD_REPLACEMENTS and REPLACEMENTS variables.
    Both of these variables are dicts where keys are regular expressions and keys are:
    - strings: for direct replacements
    - handlers: functions acception Match as argument and returning Optional[str]
    - tuples of strings or handlers: one item is selected with equal probabilities
    - dicts where keys are strings or handlers and values are relative probabilities

    Additional notes:
    In case None is selected, match remains untouched.

    If sum of dict probabilities < 1, None is added with probability 1 - SUM.
    Dict probabilities can be dynamic, callables accepting int (severity value).

    You can see examples of accents in same folder. OwO is one of the most advanced
    accents where most features are used.
    """

    # overridable variables
    WORD_REPLACEMENTS: Dict[Union[re.Pattern[str], str], Any] = {}
    REPLACEMENTS: Dict[Union[re.Pattern[str], str], Any] = {}

    # public variables
    # shortcuts for common regexes
    MESSAGE_START = r"\A(?!```)"
    MESSAGE_END = r"(?<!```)\Z"

    # private class variables
    _registered_accents: Dict[str, Accent] = {}

    def __init_subclass__(cls, is_accent: bool = True):
        super().__init_subclass__()

        if is_accent:
            instance = cls()
            cls._registered_accents[str(instance).lower()] = instance

    def __init__(self) -> None:
        self._replacemtns: Sequence[Replacement] = []

        for k, v in self.WORD_REPLACEMENTS.items():
            self._replacemtns.append(Replacement(rf"\b{k}\b", v))

        for k, v in self.REPLACEMENTS.items():
            self._replacemtns.append(Replacement(k, v))

    @classmethod
    def all_accents(cls) -> Sequence[Accent]:
        return list(cls._registered_accents.values())

    @classmethod
    def get_by_name(cls, name: str) -> Accent:
        return cls._registered_accents[name.lower()]

    def apply(
        self,
        text: str,
        *,
        severity: int = 1,
        limit: int = 2000,
        context_id: Any = None,
    ) -> str:
        context = ReplacementContext(id=context_id)
        for replacement in self._replacemtns:
            text = replacement.apply(
                text,
                severity=severity,
                limit=limit,
                context=context,
            )

        return text

    def __str__(self) -> str:
        return self.__class__.__name__
