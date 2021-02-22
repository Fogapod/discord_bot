from typing import Any

from .accent import Accent


class Reversed(Accent):
    def apply(self, text: str, *, severity: int = 1, **kwargs: Any) -> str:
        return text[::-1]
