# original accent created by: IlinMihail
# commit: https://github.com/Fogapod/pink/commit/ff46d56a4c258d9597a731c678dcb71d9fa43999


import re
import random

from pink_accents import Match, Accent

ending = (
    "thing",
    "-o-mat",
    "-o-meter",
    "destroyer",
    "tool",
    "box",
    "burger",
    "salad",
    "cola",
    "fruit",
    "cat",
    "dog",
    "bird",
    "frog",
    "pulsar",
    "beam",
    "particle",
    "wave",
    "accelerator",
    "matter",
    "void",
    "bullshit",
)
start = (
    "black",
    "white",
    "red",
    "green",
    "yellow",
    "blue",
    "cyan",
    "fap",
    "zap",
    "flap",
    "clap",
    "crap",
    "carp",
    "robo",
    "auto",
    "electro",
    "quantum",
    "recta",
    "hexa",
    "hollow",
    "light",
    "heavy",
    "super",
    "mega",
    "fancy",
    "secret",
    "bloody",
    "murder",
    "bone",
    "metal",
    "wooden",
    "stone",
    "glass",
    "soft",
    "hard",
    "hot",
    "cold",
    "liquid",
    "solid",
)
topics = (
    "weather is great today, isnt it?",
    "I ate macaronis with cheese today.",
    "oh boy, regex is so complicated!",
    "I like pineapples.",
    "have you watched this movie? Its named... Ah, forgot.",
    "you noticed how prices sky rocketed? Ramen costs 7$ now!",
    "AAAAAAAAAH!",
    "you look great today!",
)
topic_end = (
    "Ah, sorry, back to the topic...",
    "Uh... Where had we stopped?",
    "Oh sorry, Im talking about random stuff again?",
    "Ah, almost forgot about our talk!",
)


def switch_topic(m: Match) -> str:
    return f"{m.original} {random.choice(topics)} {random.choice(topic_end)}"


def repeat_word(m: Match) -> str:
    n = random.randint(0, 1) + m.severity - 1

    return f"{m.original}, {', '.join(m.original for _ in  range(n))}"


def generate_neologism(m: Match) -> str:
    return f"{random.choice(start)}{random.choice(ending)}"


class Schizophrenia(Accent):
    """Weather is great today, isnt it?"""

    WORDS = {
        r"\w+": {
            switch_topic: 0.13,
            repeat_word: 0.2,
        },
        # if new word matches any from 'ending' list its replaced by 'generate_neologism()'
        f"({'|'.join(re.escape(word) for word in ending)})": generate_neologism,
    }
