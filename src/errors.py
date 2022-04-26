# simple reexport of stuff from errorhandler cog

__all__ = ("PINKError",)

try:
    from src.cogs.utils.errorhandler import PINKError
except ImportError:
    print("utils.errorhandler cog is required")

    raise
