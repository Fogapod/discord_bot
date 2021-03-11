CREATE MIGRATION m1s4ux2ifvuqj6lilfn7fvnpjo2axgze7ebrlbvvjoh5nzs7zafeeq
    ONTO initial
{
  CREATE SCALAR TYPE default::snowflake EXTENDING std::int64;
  CREATE TYPE default::AccentSettings {
      CREATE PROPERTY accents -> array<tuple<name: std::str, severity: std::int16>> {
          SET default := (<array<tuple<name: std::str, severity: std::int16>>>[]);
      };
      CREATE REQUIRED PROPERTY guild_id -> default::snowflake;
      CREATE REQUIRED PROPERTY user_id -> default::snowflake;
      CREATE PROPERTY exclusive_hack {
          USING ((.user_id, .guild_id));
          CREATE CONSTRAINT std::exclusive;
      };
  };
  CREATE TYPE default::GuildSettings {
      CREATE REQUIRED PROPERTY guild_id -> default::snowflake;
      CREATE REQUIRED PROPERTY prefix -> std::str;
  };
};
