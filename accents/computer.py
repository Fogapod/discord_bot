from base64 import b64encode, b85encode
from typing import Any
from hashlib import sha256

from pink_accents import Accent

MORSE_CODE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
}


class Computer(Accent):
    """Computer talk."""

    @staticmethod
    def binary(text: str) -> str:
        return "".join(f"{ord(c):08b} " for c in text)

    @staticmethod
    def base64(text: str) -> str:
        return b64encode(text.encode()).decode()

    @staticmethod
    def base85(text: str) -> str:
        return b85encode(text.encode()).decode()

    @staticmethod
    def sha256(text: str) -> str:
        return sha256(text.encode()).hexdigest()

    @staticmethod
    def morse(text: str) -> str:
        return "".join(MORSE_CODE.get(c.upper(), c) for c in text)

    def apply(self, text: str, **kwargs: Any) -> str:
        algos = {
            1: self.binary,
            2: self.base64,
            3: self.base85,
            4: self.morse,
            # TODO
            10: self.sha256,
        }

        return algos.get(self.severity, self.sha256)(text)
