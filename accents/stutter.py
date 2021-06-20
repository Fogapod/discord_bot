import random

from typing import Optional

from pink_accents import Match, Accent


def repeat_char(m: Match) -> Optional[str]:
    if random.random() * m.severity < 0.2:
        return None

    severity = random.randint(0, 2) + m.severity

    return f"{'-'.join(m.original for _ in range(severity))}"


# https://github.com/unitystation/unitystation/blob/cf3bfff6563f0b3d47752e19021ab145ae318736/UnityProject/Assets/Resources/ScriptableObjects/Speech/CustomMods/Stuttering.cs
class Stutter(Accent):
    """You st-t-tart repeating some ch-h-hars."""

    PATTERNS = {
        r"\b[a-z](?=[a-z]|\s)": repeat_char,
    }
