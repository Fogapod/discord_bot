from pink_accents import Accent


class Mime(Accent):
    PATTERNS = {
        # https://stackoverflow.com/a/11324894
        #
        # this regex is not perfect, ("*abc", "abc*", "ab*c") do not match
        # r"(?<![\*\S])[^\*\s]+(?![\*\S])": "",
        r"[\s\S]+": lambda m: m.original
        if m.original.endswith("*") and m.original.startswith("*")
        else "",
        # we deleted all message content, not good
        r"\A\s*\Z": (
            # TODO: more actions
            "\u200b",
            "** **",
            "*waves*",
            "*smiles*",
            "*looks at you in confusion*",
            "*shakes head*",
            "*laughts*",
            "*sips from bottle of nothing*",
            "*draws circles in the air*",
            "*hands you invisible box*",
            "*sits on invisible chair*",
            "*tries to break through invisible wall*",
            "*touches invisible wall with both hands*",
            "*leans on invisible wall*",
            "*points up*",
            "*points down*",
            "*shoots at you from finger gun*",
            "*appears to talk but you can't hear a single word*",
        ),
    }
