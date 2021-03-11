import random

from typing import Optional

from .accent import Match, Accent

HICCBURPS = (
    "- burp... ",
    "- hic -",
    "- hic! ",
    "- buuuurp... ",
)


def duplicate_char(m: Match) -> Optional[str]:
    if random.random() * m.severity < 0.2:
        return None

    return m.original * (random.randint(0, 5) + m.severity)


def hiccburp(m: Match) -> Optional[str]:
    if random.random() * m.severity < 0.1:
        return None

    return random.choice(HICCBURPS)


# https://github.com/unitystation/unitystation/blob/cf3bfff6563f0b3d47752e19021ab145ae318736/UnityProject/Assets/Resources/ScriptableObjects/Speech/CustomMods/SlurredMod.cs
class Drunk(Accent):
    REPLACEMENTS = {
        r" +": hiccburp,
        r"[aeiouslnmr]": duplicate_char,
    }
