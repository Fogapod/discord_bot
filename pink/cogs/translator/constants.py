from typing import Mapping

import googletrans

LANGUAGES = {
    "cn": "chinese",
    **googletrans.LANGUAGES,
}

LANGCODE_ALIASES = {
    "cn": "zh-cn",
}

LANGCODES: Mapping[str, str] = {v: k for k, v in LANGUAGES.items()}
