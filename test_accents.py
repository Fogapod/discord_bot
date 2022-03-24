from pathlib import Path
from timeit import timeit

import pink_accents_rs

from pink_accents import Accent, load_from

inp = "yeah test yeah"


load_from(Path("accents"))
accents = {a.name: a for a in Accent.get_all_accents()}
scotsman = accents["Scotsman"]()

print(scotsman.apply(inp))
print(timeit("scotsman.apply(inp)", globals=locals(), number=10000))


print(pink_accents_rs.apply_accent("scotsman", inp, 1))
print(timeit("pink_accents_rs.apply_accent('scotsman', inp, 1)", globals=locals(), number=10000))
