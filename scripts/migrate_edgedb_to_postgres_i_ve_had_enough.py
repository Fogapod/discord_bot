import asyncio
import sys

import asyncpg
import edgedb  # type: ignore

sys.path.append(".")

from src.settings import settings


async def main() -> None:
    edb = await edgedb.create_async_pool(
        host=settings.database.host,
        port=settings.database.port,
        user=settings.database.user,
        password=settings.database.password,
        database=settings.database.database,
    )
    pg = await asyncpg.create_pool(
        host=input("host: ") or "localhost",
        port=int(input("port: ") or 5432),
        user=input("user: "),
        password=input("password: "),
        database=input("database: "),
    )

    for guild in await edb.query(
        """
        SELECT Prefix {
            guild_id,
            prefix,
        }
        """
    ):
        await pg.fetchrow(  # type: ignore
            "INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            guild.guild_id,
            guild.prefix,
        )

    for accents in await edb.query(
        """
        SELECT AccentSettings {
            guild_id,
            user_id,
            accents,
        }
        """
    ):
        for accent in accents.accents:
            await pg.fetchrow(  # type: ignore
                "INSERT INTO accents (guild_id, user_id, name, severity) VALUES ($1, $2, $3, $4) "
                "ON CONFLICT DO NOTHING",
                accents.guild_id,
                accents.user_id,
                accent.name,
                accent.severity,
            )

    await edb.aclose()
    await pg.close()  # type: ignore


if __name__ == "__main__":
    asyncio.run(main())
