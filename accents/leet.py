from pink_accents import Accent


class Leet(Accent):
    """1337 talk."""

    # note:
    # \ should be avoided because it renders differently in discord codeblocks and
    # normal text
    PATTERNS = {
        r"a": "4",
        r"b": "6",
        # r"c": "(",
        # r"d": "[)",
        r"e": "3",
        # r"f": "]]=",
        r"g": "&",
        # r"h": "#",
        r"i": "!",
        # r"j": ",|",
        # r"k": "]{",
        r"l": "1",
        # r"m": "(√)",
        # r"n": "(']",
        r"o": "0",
        # r"p": "|°",
        # r"q": "(,)",
        # r"r": "2",
        r"s": "$",
        r"t": "7",
        # r"u": "(_)",
        # r"v": "\/",
        # r"w": "'//",
        r"x": "%",
        # r"y": "'/",
        r"z": "2",
    }
