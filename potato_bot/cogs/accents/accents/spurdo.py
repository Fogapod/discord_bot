import random

from .accent import Accent


class Spurdo(Accent):
    REPLACEMENTS = {
        r"xc": "gg",
        r"c": "g",
        r"k": "g",
        r"t": "d",
        r"p": "b",
        r"x": "gs",
        r"\Bng\b": "gn",
        r":?\)+": lambda m: f":{'D' * len(m.original) * (random.randint(1, 5) + m.severity)}",
        Accent.MESSAGE_END: {
            lambda m: f" :{'D' * (random.randint(1, 5)+ m.severity)}": 0.5,
        },
    }

    WORD_REPLACEMENTS = {
        r"epic": "ebin",
    }
