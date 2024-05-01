import asyncio
import sqlite3

from pathlib import Path

import asyncpg


async def main() -> None:
    pg = await asyncpg.create_pool(
        host=input("host: ") or "localhost",
        port=int(input("port: ") or 5432),
        user=input("user: "),
        password=input("password: "),
        database=input("database: "),
    )

    sqlite_path = input("sqlite path: ")
    conn = sqlite3.connect(sqlite_path)
    db = conn.cursor()

    with Path("schema.sql").open() as f:
        db.executescript(f.read())

    prefixes = [r async for r in pg.fetch("SELECT * FROM prefixes")]
    print("inserting", len(prefixes), "prefixes")
    db.executemany("INSERT INTO prefixes (guild_id, prefix) VALUES (?, ?)", prefixes)

    accents = [r async for r in pg.fetch("SELECT * FROM accents")]
    print("inserting", len(accents), "accents")
    db.executemany("INSERT INTO accents (guild_id, user_id, name, severity) VALUES (?, ?, ?, ?)", accents)

    conn.commit()


if __name__ == "__main__":
    asyncio.run(main())
