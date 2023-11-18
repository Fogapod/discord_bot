from _shared import DISCORD_MESSAGE_END  # type: ignore[import-not-found]
from pink_accents import Accent


class Slav(Accent):
    """You feel drunk"""

    WORDS = {  # noqa: RUF012
        r"my": "our",
        r"friend": "comrade",
        r"(enemy|foe)": "american pig",
        r"(fuck|shit)": (
            "blyat",
            "cyka",
        ),
        r"usa": "американские захватчики",
        r"we are being attacked": "нас атакуют",
    }

    PATTERNS = {  # noqa: RUF012
        r"\b(a|the) +": {
            "": 0.5,
        },
        r"\bha": "ga",
        r"e(?!e)": "ye",
        r"th": ("z", "g"),
        r"\Bo?u": ("a", "oo"),
        r"w": "v",
        DISCORD_MESSAGE_END: {
            " blyat": 0.5,
        },
    }
