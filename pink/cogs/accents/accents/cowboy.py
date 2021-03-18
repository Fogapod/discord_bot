import random

from typing import Optional

from .accent import Match, Accent


def yeehaw(m: Match) -> Optional[str]:
    if random.random() > m.severity / 10:
        return None

    return f"y{'e'* (random.randint(0,5) + m.severity)}haw"


# https://en.m.wikipedia.org/wiki/Texan_English
# https://lingojam.com/CowboyTalkTranslator
# Is pretty bad, needs rework
class Cowboy(Accent):
    REPLACEMENTS = {
        r"\bo\B": "aw",
        # "the" excluded
        r"\b(th|t)(?!h?e\b)\B": "'",
        r"\Bng\b": "n'",
        r"\Bd\b": "",
        r"\Bht\b": "hyt",
        # exclude "hey"
        r"\B(?<!\bh)ey\b": "ay",
        r"(?<=g)r\B": "uh-r",
        r"(?<!h-)re": "hr",
        Accent.MESSAGE_END: lambda m: f" {yeehaw(m)}",
    }
    WORD_REPLACEMENTS = {
        r"the": "thuh",
        r"hey": ("heya", "ee", "hay"),
        r"you": ("cha", "chu", "ya"),
        r"buzzard": "vulture",
        r"dogie": "calf",
        r"about to": "fixin' to",
        r"(hello|hi|how do you do)": "howdy",
        r"you all": "y'all",
        r"bull": "toro",
        r"(freezer|refrigerator)": "ice box",
    }
