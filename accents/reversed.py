from typing import Any

from pink_accents import Accent


class Reversed(Accent):
    """.txet sesreveR"""

    def apply(self, text: str, **kwargs: Any) -> str:
        return text[::-1]
