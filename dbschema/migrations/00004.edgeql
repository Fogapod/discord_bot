CREATE MIGRATION m1t5po3prd7zn3pqceoq2gtmsllgyncgrkop6evvzc3c2o4ccrapxa
    ONTO m1tqngnmntnyrlpqst6ski3qlwy344wm4xba4vnvjaptfhb5lgfb4a
{
  ALTER TYPE default::GuildSettings RENAME TO default::Prefix;
  ALTER TYPE default::Prefix {
      ALTER PROPERTY prefix {
          SET REQUIRED USING (',');
      };
  };
};
