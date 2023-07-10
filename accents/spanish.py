# original accent from Space Station 14:
# https://github.com/space-wizards/space-station-14/blob/84616743e99cec8dfcff7e3418bde4a57b27b8cd/Content.Server/Speech/Components/SpanishAccentComponent.cs

import re

from typing import Any

from pink_accents import Accent


class Spanish(Accent):
    """¿QUIERES?"""

    _sentence_end = re.compile(r"(?<=[\.!\?])")
    _first_non_space = re.compile(r"(?=\S)")

    PATTERNS = {  # noqa: RUF012
        r"((?<=\s)|\A)s": "es",
    }

    def apply(self, text: str, **kwargs: Any) -> str:
        text = super().apply(text, **kwargs)

        result = ""

        for sentence in self._sentence_end.split(text):
            if sentence.endswith("?"):
                spaces, sentence = self._first_non_space.split(sentence, maxsplit=1)
                result += f"{spaces}¿{sentence}"
            else:
                result += sentence

        return result
