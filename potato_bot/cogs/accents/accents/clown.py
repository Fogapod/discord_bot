import random

from typing import Optional

from .accent import Match, Accent


def honk(m: Match) -> Optional[str]:
    n = random.randint(0, 3) + m.severity

    return f"{' HONK' * n}!"


# https://github.com/unitystation/unitystation/blob/cf3bfff6563f0b3d47752e19021ab145ae318736/UnityProject/Assets/Resources/ScriptableObjects/Speech/Clown.asset
class Clown(Accent):
    REPLACEMENTS = {
        r"[a-z]+": lambda m: m.original.upper() if m.severity > 1 else m.original,
        Accent.MESSAGE_END: honk,
    }
