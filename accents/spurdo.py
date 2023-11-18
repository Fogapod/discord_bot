import random

from _shared import DISCORD_MESSAGE_END  # type: ignore[import-not-found]
from pink_accents import Accent


class Spurdo(Accent):
    """You want to run away into forest"""

    PATTERNS = {  # noqa: RUF012
        r"xc": "gg",
        r"c": "g",
        r"k": "g",
        r"t": "d",
        r"p": "b",
        r"x": "gs",
        r"\Bng\b": "gn",
        r":?\)+": lambda m: f":{'D' * len(m.original) * (random.randint(1, 5) + m.severity)}",
        DISCORD_MESSAGE_END: {
            lambda m: f" :{'D' * (random.randint(1, 5)+ m.severity)}": 0.5,
        },
    }

    WORDS = {  # noqa: RUF012
        r"epic": "ebin",
    }
