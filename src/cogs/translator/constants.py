from typing import Mapping

import googletrans

LANGUAGES = {
    "cn": "chinese",
    **googletrans.LANGUAGES,
}

LANGCODE_ALIASES = {
    "cn": "zh-cn",
}

REVERSE_LANGCODE_ALIASES = {v: k for k, v in LANGCODE_ALIASES.items()}

LANGCODES: Mapping[str, str] = {v: k for k, v in LANGUAGES.items()}
