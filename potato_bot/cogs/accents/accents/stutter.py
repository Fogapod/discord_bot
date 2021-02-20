import random

from typing import Optional

from .accent import Match, Accent


# https://github.com/unitystation/unitystation/blob/cf3bfff6563f0b3d47752e19021ab145ae318736/UnityProject/Assets/Resources/ScriptableObjects/Speech/CustomMods/Stuttering.cs
class Stutter(Accent):
    def repeat_char(m: Match) -> Optional[str]:
        if random.random() * m.severity < 0.2:
            return

        severity = random.randint(0, 2) + m.severity

        return f"{'-'.join(m.original for _ in range(severity))}"

    REPLACEMENTS = {
        r"\b[a-z](?=[a-z]|\s)": repeat_char,
    }
