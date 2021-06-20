from pink_accents import Accent


class Dyslexic(Accent):
    """Swaps some words lettesr and."""

    PATTERNS = {
        # swap words with 5% * severity chance
        r"\b(\w+?)(\s+)(\w+?)\b": {
            lambda m: f"{m.match[3]}{m.match[2]}{m.match[1]}": lambda s: s * 0.05,
            None: 0.95,
        },
        # swap letters with 5% * severity chance
        # NOTE: lower() is used to let the replace function handle case
        r"[a-z]{2}": {
            lambda m: m.original[::-1].lower(): lambda s: s * 0.05,
            None: 0.95,
        },
    }
