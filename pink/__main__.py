import os
import logging

from .bot import Bot

log = logging.getLogger(__name__)

if __name__ == "__main__":
    if sentry_dsn := os.environ.get("SENTRY_DSN"):
        import sentry_sdk

        sentry_sdk.init(
            sentry_dsn,
            traces_sample_rate=1.0,
        )
    else:
        log.warning("skipped sentry initialization")

    bot = Bot()

    bot.run(os.environ["BOT_TOKEN"])
