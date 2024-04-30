#!/bin/sh

# this is a manual scipt while i build some CD
podman pull docker.io/fogapod/pink
podman run --replace --name pink-bot --restart always -v ${PWD}/settings.toml:/code/settings.toml -v pink_bot_db:/code/pink.db --hostname pink_prod --network host -d docker.io/fogapod/pink
