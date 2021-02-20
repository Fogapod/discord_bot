import random

from .accent import Match, Accent, ReplacementContext

CURSED_ES = "EĒÊËÈÉ"

# arbitrary number, ideally should be equal to average message length
CHOICES_STEP = 30


# This is my attempt to optimize accent by not calling random.choice(CURSED_ES) for
# each letter. Instead, I call random.choices at an interval and store result in
# context
#
# state in this case is a list of 2 items where first is pointer and second is an
# array of es
def next_cursed_e(ctx: ReplacementContext) -> str:
    if ctx.state is None or ctx.state[0] == CHOICES_STEP:
        ctx.state = [0, random.choices(CURSED_ES, k=CHOICES_STEP)]

    letter = ctx.state[1][ctx.state[0]]

    ctx.state[0] += 1

    return letter


def e(m: Match):
    if m.severity < 5:
        return "e"

    elif m.severity < 10:
        return "E"

    return next_cursed_e(m.context)


class E(Accent):
    REPLACEMENTS = {
        r"[a-z]": e,
    }
