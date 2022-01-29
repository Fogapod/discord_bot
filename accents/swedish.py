import random

from typing import Optional

from _shared import DISCORD_MESSAGE_END
from pink_accents import Accent, Replacement


def bork(severity: int) -> Optional[str]:
    if random.random() * severity < 1 / 3:
        return None

    return f" bork{', bork' * random.randint(0, severity)}!"


SEVERE_PATTERNS = {
    r"a": (
        "å",
        "ä",
        "æ",
        "a",
    ),
    r"o": (
        "ö",
        "ø",
        "o",
    ),
}


# https://github.com/unitystation/unitystation/blob/cf3bfff6563f0b3d47752e19021ab145ae318736/UnityProject/Assets/Resources/ScriptableObjects/Speech/Swedish.asset
class Swedish(Accent):
    """You feel the urge to build a meatball monument"""

    PATTERNS = {
        r"w": "v",
        r"j": "y",
        r"bo": "bjo",
    }

    def register_patterns(self) -> None:
        super().register_patterns()

        bork_severity = self.severity

        if self.severity >= 6:
            # resets at accent severity 6
            bork_severity = self.severity - 5

            for k, v in SEVERE_PATTERNS.items():
                self.register_replacement(Replacement(k, v))

        if bork_severity > 1:
            self.register_replacement(
                Replacement(DISCORD_MESSAGE_END, lambda _: bork(bork_severity))
            )
