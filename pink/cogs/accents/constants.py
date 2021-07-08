from pathlib import Path

from pink_accents import Accent, load_from

load_from(Path("accents"))


ALL_ACCENTS = {
    a.name.lower(): a for a in sorted(Accent.get_all_accents(), key=lambda a: a.name)
}
