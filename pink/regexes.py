import re

# https://github.com/Fogapod/KiwiBot/blob/master/constants.py

# theoretical shortest snowflake is 15 characters, but shortest known one is 21154535154122752
_ID_EXPR = r"\d{17,19}"

_USER_MENTION_EXPR = fr"<@!?({_ID_EXPR})>"
_ROLE_MENTION_EXPR = fr"<@&({_ID_EXPR})>"
_CHANNEL_MENTION_EXPR = fr"<#({_ID_EXPR})>"

# NOTE: name length is {1,32} instead of {2,32} because bots can send 1 letter emotes
_EMOTE_EXPR = fr"<(?P<animated>a?):(?P<name>[_a-zA-Z0-9]{{1,32}}):(?P<id>{_ID_EXPR})>"

ID_REGEX = re.compile(_ID_EXPR)
USER_MENTION_REGEX = re.compile(_USER_MENTION_EXPR)
ROLE_MENTION_REGEX = re.compile(_ROLE_MENTION_EXPR)
CHANNEL_MENTION_REGEX = re.compile(_CHANNEL_MENTION_EXPR)
EMOTE_REGEX = re.compile(_EMOTE_EXPR)

USER_MENTION_OR_ID_REGEX = re.compile(fr"(?:{_USER_MENTION_EXPR})|{_ID_EXPR}")
ROLE_OR_ID_REGEX = re.compile(fr"(?:{_ROLE_MENTION_EXPR})|{_ID_EXPR}")
CHANNEL_OR_ID_REGEX = re.compile(fr"(?:{_CHANNEL_MENTION_EXPR})|{_ID_EXPR}")

CLEAN_URL_REGEX = re.compile(r"\A<|>\Z")
