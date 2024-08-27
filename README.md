# PINK Discord bot

PINK Is Not Kiwi.

This is a personal discord bot that has a few commands related to Unitystation. I have put minimal effort into it because of how bad Discord have become lately. 0 funnies included.

## Running PINK

Rough instructions:

Building podman/docker image: `podman build . -t fogapod/pink` (no tricks)  
Running podman/docker image: `podman run --rm --name pink -v $(pwd)/settings.toml:/code/settings.toml -v $(pwd)/pink.db:/data/pink.db fogapod/pink`

Running on production:

- fill in settings.toml file
- create sqlite database from `schema.sql`
- start service from units/
