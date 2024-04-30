CREATE TABLE IF NOT EXISTS prefixes (
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS accents (
    guild_id BIGINT,
    user_id BIGINT,
    name VARCHAR(64),
    severity SMALLINT NOT NULL,

    PRIMARY KEY (guild_id, user_id, name)
);
