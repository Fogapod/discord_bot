import logging
import logging.config

__all__ = ("setup_logging",)

LEVEL_TO_COLOR_VALUE = {
    # green
    logging.INFO: "32",
    # yellow
    logging.WARNING: "33",
    # red
    logging.ERROR: "31",
    # white on red
    logging.CRITICAL: "41",
}

COLOR_START = "\033["
COLOR_RESET = "\033[0m"

# -8s because CRITICAL
VERBOSE_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
SIMPLE_FORMAT = "%(levelname)-8s %(name)s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)

        if color_value := LEVEL_TO_COLOR_VALUE.get(record.levelno):
            return f"{COLOR_START}{color_value}m{formatted}{COLOR_RESET}"

        return formatted


LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "verbose": {"format": VERBOSE_FORMAT, "datefmt": DATE_FORMAT},
        "simple": {"format": SIMPLE_FORMAT},
        "colorful_verbose": {
            "()": ColorFormatter,
            "format": VERBOSE_FORMAT,
            "datefmt": DATE_FORMAT,
        },
        "colorful_simple": {"()": ColorFormatter, "format": SIMPLE_FORMAT},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "colorful_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "colorful_simple",
        },
    },
    "root": {"level": "INFO", "handlers": ["colorful_console"]},
    "disable_existing_loggers": False,
    "loggers": {
        # annoying msgpack message on init
        "aiocache": {"level": "ERROR"},
        # too verbose
        "discord": {"level": "ERROR"},
    },
}


def setup_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
