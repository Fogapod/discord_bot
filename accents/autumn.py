import random

from _shared import DISCORD_MESSAGE_END  # type: ignore[import]
from pink_accents import Accent, Match


def go_brrrr(m: Match) -> str:
    forms_of_go = (
        ("es", "goes"),
        ("e", "go"),
        ("ed", "went"),
        ("ing", "going"),
    )
    for ending, _go_form in forms_of_go:
        if m.original.lower().endswith(ending):
            break
    else:
        _go_form = forms_of_go[0][1]

    return f"{_go_form} br{'r' * random.randint(1, 10)}"


class Autumn(Accent):
    """Texan + Australian - letters = Autumn"""

    WORDS = {
        r"increas[a-z]+": {
            lambda m: go_brrrr(m): 0.5,
        },
        "them": "em",
        "well": "welp",
        "oh": {
            "er": 0.5,
        },
        "hey": "yo",
        "because": "cause",
        "let me": "lemme",
        "this is": {
            "dis": 0.2,
            "tis": 0.3,
        },
    }
    PATTERNS = {
        # "who" does not work well with this
        r"\bwh(?!o)": "w",
        r"oo": "u",
        # !!contextual syntax is hell!!
        # I'm not sure how to describe this rule universally yet
        # some examples:
        # + something
        # + nothing
        # + doing
        # - thing
        # - wrong
        #
        # blacklisting all bad examples for now
        r"(?<!\b(?:thi|wro))ng\b": (
            "n",
            "n'",
        ),
        r"'?ve been": "da",
        r"disappear": "poof",
        DISCORD_MESSAGE_END: {
            " ye daft cunt": 0.02,
        },
    }
