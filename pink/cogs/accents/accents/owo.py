import math
import random

from .accent import Match, Accent

NYAS = (
    ":3",
    ">w<",
    "^w^",
    "owo",
    "OwO",
    "nya",
    "Nya",
    "nyan",
    "!!!",
    "(=^‥^=)",
    "(=；ｪ；=)",
    "ヾ(=｀ω´=)ノ”",
    "~~",
    "*wings their tail*",
    "\N{PAW PRINTS}",
)

EXTREME_NYAS = (
    ";)",
    "uwu",
    "UwU",
)

ALL_NYAS = (
    *NYAS,
    *EXTREME_NYAS,
)

EXTREME_NYA_TRESHOLD = 5


def nya(m: Match) -> str:
    weights = [1] * len(NYAS)

    if m.severity > EXTREME_NYA_TRESHOLD:
        weights += [m.severity - EXTREME_NYA_TRESHOLD] * len(EXTREME_NYAS)
    else:
        weights += [0] * len(EXTREME_NYAS)

    return " ".join(
        random.choices(ALL_NYAS, weights)[0]
        for _ in range(random.randint(0, max((1, round(m.count_logarithmic() * 5)))))
    )


def logarithmic_owo(s: int) -> float:
    return max((0.25, math.log10(s)))


class OwO(Accent):
    REPLACEMENTS = {
        r"[rlv]": "w",
        r"ove": "uv",
        r"(?<!ow)o(?!wo)": {
            "owo": 0.2,
        },
        # do not break mentions by avoiding @
        r"(?<!@)!": lambda m: f" {random.choice(NYAS)}!",
        r"ni": "nyee",
        r"na": "nya",
        r"ne": "nye",
        r"no": "nyo",
        r"nu": "nyu",
        Accent.MESSAGE_START: {
            lambda m: f"{nya(m)} ": logarithmic_owo,
            None: 1,
        },
        Accent.MESSAGE_END: {
            lambda m: f" {nya(m)}": logarithmic_owo,
            None: 1,
        },
    }
