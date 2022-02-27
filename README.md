# PINK Discord bot
PINK Is Not Kiwi.

This is a personal discord bot that has a few commands related to Unitystation. I have put minimal effort into it because of how bad Discord have become lately. 0 funnies included.

### Running PINK
Since I no longer maintain this, you will need an outdated beta2 edgedb version. This will be annoying to get and set up. Rough instructions:

Building podman/docker image: `podman build . -t fogapod/pink` (no tricks)
Running podman/docker image: `podman run --rm --name pink -v $(pwd):/code fogapod/pink` (dev version, bind entire repo inside container)

Running on production:
- get edgedb beta 2 somewhere
- edgedb server init pink
- edgedb -I pink create-superuser-role pink --password (enter password)
- fill in .env file
- start service from units/
