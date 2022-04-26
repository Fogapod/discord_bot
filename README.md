# PINK Discord bot

PINK Is Not Kiwi.

This is a personal discord bot that has a few commands related to Unitystation. I have put minimal effort into it because of how bad Discord have become lately. 0 funnies included.

## Running PINK

Rough instructions:

Building podman/docker image: `podman build . -t fogapod/pink` (no tricks)
Running podman/docker image: `podman run --rm --name pink -v $(pwd):/code fogapod/pink` (dev version, bind entire repo inside container)

Running on production:

- install postgres
- apply schema.sql
- fill in settings.toml file
- start service from units/
