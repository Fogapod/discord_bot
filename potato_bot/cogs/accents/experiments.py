from .accent import Accent


class Arabic(Accent):
    WORD_REPLACEMENTS = {
        "god": "Allah",
        "good": "halal",
        "bad": "haram",
        # TODO
        "(man|orange)": "Ben Shapiro",
        "the": (
            "arabic",
            "arabe",
        ),
    }

    REPLACEMENTS = {
        r"ic": "e",
        r"c": "g",
        r"t\b": "to",
    }


class TrumpScript(Accent):
    WORD_REPLACEMENTS = {
        "true": "fact",
        "false": "lie",
        "print": (
            "tell",
            "say",
        ),
        "while": "as long as",
    }

    REPLACEMENTS = {
        r"\+": "plus",
        r"\-": "minus",
        r"(?<=\s)\*(?=\s)": "times",
        r"/": "over",
        r"(?<=\s)<(?=\s)": (
            "less",
            "fewer",
            "smaller",
        ),
        r"(?<=\s)>(?=\s)": (
            "more",
            "greater",
            "larger",
        ),
        Accent.MESSAGE_END: " America is great",
    }
