from pink_accents import Accent

# probably related:
# https://github.com/python/typing/issues/760
# for some reason mypy does not understand that str can be compared
ALL_ACCENTS = {
    a.name.lower(): a for a in sorted(Accent.get_all_accents(), key=lambda a: a.name)  # type: ignore
}
