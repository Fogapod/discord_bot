# original accent created by: PotatoAlienOf13
# commit: https://github.com/PotatoStation/discord_bot/commit/f7bdfa0b9603384dbc58c108ad3bdf942bb61baa

from pink_accents import Accent


class Dashes(Accent):
    """Who-even-talks-like-this?"""

    PATTERNS = {  # noqa: RUF012
        r" +": "-",
    }
