from .accent import Accent


class Scotsman(Accent):
    REPLACEMENTS = {
        Accent.MESSAGE_END: {
            " ye daft cunt": 0.5,
        }
    }
