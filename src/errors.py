# simple reexport of stuff from errorhandler cog

import logging

__all__ = ("PINKError",)

log = logging.getLogger(__name__)

try:
    from src.cogs.utils.errorhandler import PINKError
except ImportError:
    log.critical("errorhandler cog is required")

    raise
