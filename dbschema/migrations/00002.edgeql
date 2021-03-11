CREATE MIGRATION m1bwwtn5kb7iuojymql2ej6kny73r6uhdgq24ezmawbgintz4nvc3q
    ONTO m1s4ux2ifvuqj6lilfn7fvnpjo2axgze7ebrlbvvjoh5nzs7zafeeq
{
  ALTER TYPE default::GuildSettings {
      ALTER PROPERTY guild_id {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
