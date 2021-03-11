CREATE MIGRATION m1tqngnmntnyrlpqst6ski3qlwy344wm4xba4vnvjaptfhb5lgfb4a
    ONTO m1bwwtn5kb7iuojymql2ej6kny73r6uhdgq24ezmawbgintz4nvc3q
{
  ALTER TYPE default::GuildSettings {
      ALTER PROPERTY prefix {
          RESET OPTIONALITY;
      };
  };
};
