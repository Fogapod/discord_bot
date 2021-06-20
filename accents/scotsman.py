from _shared import DISCORD_MESSAGE_END
from pink_accents import Accent


class Scotsman(Accent):
    """Somewhat rude accent."""

    PATTERNS = {
        DISCORD_MESSAGE_END: {
            " ye daft cunt": lambda s: 0.4 + (0.6 * s / 9),
        }
    }
