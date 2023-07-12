import asyncio
import logging
import platform

import aiohttp
import asyncpg
import discord
import redis.asyncio as redis

from .bot import PINK
from .logging import setup_logging
from .settings import settings
from .version import Version

log = logging.getLogger(__name__)

try:
    import uvloop
except ImportError:
    print("uvloop is not installed")
else:
    uvloop.install()


async def main() -> None:
    setup_logging()

    version = Version()

    log.info("running on version %s python %s", version.full(), platform.python_version())

    if settings.sentry.dsn is not None:
        import sentry_sdk

        sentry_sdk.init(
            settings.sentry.dsn,
        )
    else:
        log.warning("skipped sentry initialization")

    session = aiohttp.ClientSession(headers={"user-agent": "PINK bot"})
    pg = asyncpg.create_pool(
        host=settings.database.host,
        port=settings.database.port,
        user=settings.database.user,
        password=settings.database.password,
        database=settings.database.database,
    )
    rd: redis.Redis[bytes] = redis.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
    )

    pink = PINK(
        session=session,
        pg=pg,
        redis=rd,
        version=version,
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

    async with pink, session, pg, rd:
        await pink.start(settings.bot.token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("KeyboardInterrupt")
