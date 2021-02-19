import random

from typing import Optional

from .accent import Match, Accent


def honk(m: Match) -> Optional[str]:
    return f"{' HONK' * random.randint(1, 4)}!"


# https://github.com/unitystation/unitystation/blob/cf3bfff6563f0b3d47752e19021ab145ae318736/UnityProject/Assets/Resources/ScriptableObjects/Speech/Clown.asset
class Clown(Accent):
    REPLACEMENTS = {
        r"[a-z]": lambda m: m.original.upper(),
        r"(?<!```)\n": lambda m: f"{honk(m)}\n",
        Accent.MESSAGE_END: honk,
    }
