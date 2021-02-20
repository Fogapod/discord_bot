from .accent import Accent


class E(Accent):
    REPLACEMENTS = {
        r"[a-z]": lambda m: "e" if m.severity < 5 else "E",
    }
