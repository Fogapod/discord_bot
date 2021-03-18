from .accent import Accent


class Dashes(Accent):
    REPLACEMENTS = {
        r" +": "-",
    }
