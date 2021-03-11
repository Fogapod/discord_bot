module default {
    type GuildSettings {
        required property guild_id -> snowflake;
        required property prefix -> str;
    }

    type AccentSettings {
        required property user_id -> snowflake;
        required property guild_id -> snowflake;
        property accents -> array<tuple<name: str, severity: int16>> {
            default := <array<tuple<name: str, severity: int16>>>[]
        };

        # https://github.com/edgedb/edgedb/issues/1939#issuecomment-789197413
        # constraint exclusive on ((.user_id, .guild_id));
        property exclusive_hack {
            using ((.user_id, .guild_id));
            constraint exclusive;
        };
    }

    scalar type snowflake extending int64;
};