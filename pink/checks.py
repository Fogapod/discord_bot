from typing import Callable, TypeVar

from discord.ext import commands

from .context import Context

__all__ = ("is_owner",)

T = TypeVar("T")


def is_owner() -> Callable[[T], T]:
    async def predicate(ctx: Context) -> bool:
        if ctx.author.id not in ctx.bot.owner_ids:
            raise commands.NotOwner("Must be a bot owner to use this")

        return True

    return commands.check(predicate)
