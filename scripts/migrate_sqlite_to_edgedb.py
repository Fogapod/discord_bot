#!/usr/bin/python

import os
import json
import sqlite3

from typing import Any, Dict, List, Tuple

import edgedb

from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    sqlite_conn = sqlite3.connect("db.sqlite")
    sqlite_conn.row_factory = sqlite3.Row

    edgedb_conn = edgedb.connect(os.environ["EDGEDB_DSN"])

    accents: Dict[Tuple[int, int], List[Any]] = {}
    for accent in sqlite_conn.execute(
        "SELECT guild_id, user_id, accent, severity FROM user_accent"
    ):
        pk = (accent["guild_id"], accent["user_id"])
        data = (accent["accent"], accent["severity"])
        if pk in accents:
            accents[pk].append(data)
        else:
            accents[pk] = [data]

    for pk, data_ in accents.items():
        # json cast because tuples are not supported
        # https://github.com/edgedb/edgedb/issues/2334#issuecomment-793041555
        edgedb_conn.query(
            """
            INSERT AccentSettings {
                guild_id := <snowflake>$guild_id,
                user_id  := <snowflake>$user_id,
                accents  := <array<tuple<str, int16>>><json>$accents,
            } UNLESS CONFLICT ON .exclusive_hack
            ELSE (
                UPDATE AccentSettings
                SET {
                    accents := <array<tuple<str, int16>>><json>$accents,
                }
            )
            """,
            guild_id=pk[0],
            user_id=pk[1],
            accents=json.dumps(data_),
        )

    sqlite_conn.close()
    edgedb_conn.close()


if __name__ == "__main__":
    main()
