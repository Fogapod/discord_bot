import asyncio
import logging

import aiohttp
import discord
import edgedb

from .bot import PINK
from .logging import setup_logging
from .settings import settings

log = logging.getLogger(__name__)

try:
    import uvloop
except ImportError:
    print("uvloop is not installed")
else:
    uvloop.install()


async def main() -> None:
    setup_logging()

    if settings.sentry.dsn is not None:
        import sentry_sdk

        sentry_sdk.init(
            settings.sentry.dsn,
            traces_sample_rate=1.0,
        )
    else:
        log.warning("skipped sentry initialization")

    session = aiohttp.ClientSession(headers={"user-agent": "PINK bot"})
    edb = edgedb.create_async_pool(  # type: ignore[no-untyped-call]
        host=settings.database.host,
        port=settings.database.port,
        user=settings.database.user,
        password=settings.database.password,
        database=settings.database.database,
    )

    async with session, edb:
        pink = PINK(
            session=session,
            edb=edb,
            command_prefix=settings.bot.prefix,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
            intents=discord.Intents(
                guilds=True,
                members=True,
                emojis=True,
                messages=True,
                message_content=True,
                reactions=True,
            ),
        )

        await pink.start(settings.bot.token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("KeyboardInterrupt")
