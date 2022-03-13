import logging
import os

from .bot import PINK
from .logging import setup_logging

log = logging.getLogger(__name__)

try:
    import uvloop
except ImportError:
    print("uvloop is not installed")
else:
    uvloop.install()

if __name__ == "__main__":
    setup_logging()

    if sentry_dsn := os.environ.get("SENTRY_DSN"):
        import sentry_sdk

        sentry_sdk.init(
            sentry_dsn,
            traces_sample_rate=1.0,
        )
    else:
        log.warning("skipped sentry initialization")

    pink = PINK()
    pink.run(os.environ["BOT_TOKEN"])
