import re

import random

from .accent import Match, Accent

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


def switch_topic(m: Match):
    return " ".join(["," + random.choice(topics)] + [random.choice(topic_end)])


def repeat_word(m: Match):
    n = random.randint(1, 2)
    return " ".join(["," + m.original] * n)


def generate_neologism(m: Match):

    neologism = random.choice(start) + random.choice(ending)

    return " ".join([neologism])


class Schizophrenia(Accent):
    REPLACEMENTS = {
        r"\w+": {switch_topic: 2, repeat_word: 3, None: 10},
        f"({'|'.join(re.escape(word) for word in ending)})": generate_neologism(), #if new word matches any from 'ending' massive its replaced by 'generate_neologism()'
    }
