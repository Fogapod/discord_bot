import os

from dotenv import load_dotenv

__all__ = ("PREFIX",)

load_dotenv()

PREFIX = os.environ["BOT_PREFIX"]
