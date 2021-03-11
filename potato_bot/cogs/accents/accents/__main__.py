import sys
import importlib

from pathlib import Path

from .accent import Accent

USAGE = f"""python -m {__package__} <severity> [accent...]

Starts interactive session if used without arguments.
Lists accents if no accents provided."""


def load_accents() -> None:
    for child in Path(__file__).parent.iterdir():
        if child.suffix != ".py":
            continue

        if child.name.startswith("__"):
            continue

        if child.name == "accent.py":
            continue

        importlib.import_module(f"{__package__}.{child.stem}")


def main() -> None:
    load_accents()

    if len(sys.argv) == 1:
        for accent in Accent.all_accents():
            print(accent)

        sys.exit(0)

    if len(sys.argv) == 2:
        print(USAGE)
        sys.exit(1)

    severity = int(sys.argv[1])

    accents = set()
    for arg in sys.argv[2:]:
        try:
            accent = Accent.get_by_name(arg.lower())
        except KeyError:
            print(f"Warning: Skipping unknown accent: {arg}")
        else:
            accents.add(accent)

    if not accents:
        print("No accents matched, exiting")
        sys.exit(1)

    while True:
        try:
            text = input("> ")
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)

        for accent in accents:
            text = accent.apply(text, severity=severity)

        print(text)


if __name__ == "__main__":
    main()
