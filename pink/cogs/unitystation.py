import copy
import time
import asyncio

from typing import Any, Dict, List, Optional

from discord.ext import commands

from pink.bot import Bot
from pink.cog import Cog
from pink.context import Context
from pink.cogs.utils.errorhandler import PINKError

SERVER_FETCH_INTERVAL = 10


US_INVITE = "tFcTpBp"


class UnityStation(Cog):
    # f-strings and .format do not count as docstring
    __doc__ = f"""
    UnityStation related commands

    UnityStation is a SS13 remake in Unity.
    You can learn more about this game by joining their official server: discord.gg/{US_INVITE}
    """

    def __init__(self, bot: Bot):
        super().__init__(bot)

        self._fetched_servers_time = time.monotonic() - SERVER_FETCH_INTERVAL
        self._fetched_servers: List[Dict[str, Any]] = []

    @commands.command(aliases=["list", "sv", "ls"])
    async def servers(self, ctx: Context, *, server: Optional[str] = None) -> None:
        """List hub servers"""

        async with ctx.typing():
            if server is None:
                await self._servers(ctx)
            else:
                await self._server(ctx, server)

    async def _fetch_servers(self, ctx: Context) -> List[Dict[str, Any]]:
        if time.monotonic() - self._fetched_servers_time < SERVER_FETCH_INTERVAL:
            return copy.deepcopy(self._fetched_servers)

        async with ctx.session.get("https://api.unitystation.org/serverlist") as r:
            if r.status != 200:
                raise PINKError(f"Bad API response status code: **{r.status}**")

            # they send json with html mime type
            data = await r.json(content_type=None)

        # sort using player count and name fields, player count is reversed and is more
        # significant
        servers = sorted(
            data["servers"], key=lambda s: (-s["PlayerCount"], s["ServerName"])
        )

        self._fetched_servers_time = time.monotonic()
        self._fetched_servers = servers

        return copy.deepcopy(servers)

    async def _server(self, ctx: Context, server_name: str) -> None:
        servers = await self._fetch_servers(ctx)

        server_name = server_name.lower()

        for server in servers:
            if server["ServerName"].lower().startswith(server_name):
                break
        else:
            return await ctx.send("No servers with this name")

        download_aliases = {
            "WinDownload": "windows",
            "LinuxDownload": "linux",
            "OSXDownload": "osx",
        }

        async def check_url(url: Optional[str]) -> int:
            # FIXME
            if url is None:
                return -1

            async with ctx.session.head(url) as r:
                return r.status

        # TODO: cache this like servers?
        status_codes = await asyncio.gather(
            *[check_url(server.get(name)) for name in download_aliases.keys()]
        )

        for status, key in zip(status_codes, download_aliases.keys()):
            if status != 200:
                server[key] = f"[{status}] {server[key]}"

        longest_download_name = len(
            max(download_aliases.values(), key=lambda v: len(v))
        )

        downloads = "\n".join(
            f"{alias:<{longest_download_name}} : {server.pop(name)}"
            for name, alias in download_aliases.items()
        )

        # compose address from 2 variables
        ip = server.pop("ServerIP", "unknown")
        port = server.pop("ServerPort", "unknown")

        server["address"] = f"{ip}:{port}"

        aliases = {
            "ServerName": "name",
            "ForkName": "fork",
            "BuildVersion": "build",
            "CurrentMap": "map",
            "GameMode": "gamemode",
            "IngameTime": "time",
            "PlayerCount": "players",
        }
        longest_name = len(max(server.keys(), key=lambda k: len(aliases.get(k, k))))

        main_info = "\n".join(
            f"{aliases.get(name, name):<{longest_name}} : {value}"
            for name, value in server.items()
        )

        await ctx.send(f"```\n{main_info}\n\nDownloads\n{downloads}```")

    async def _servers(self, ctx: Context) -> None:
        if not (servers := await self._fetch_servers(ctx)):
            return await ctx.send("No servers online")

        # newlines are allowed in server names
        for server in servers:
            server["ServerName"] = server.get("ServerName", "unknown").replace(
                "\n", " "
            )

        columns = {
            "Server": "ServerName",
            "Build": "BuildVersion",
            "Players": "PlayerCount",
        }

        column_widths = {}

        for col_name, col_key in columns.items():
            longest_value = str(
                sorted(servers, key=lambda x: len(str(x[col_key])))[-1][col_key]
            )

            column_widths[col_name] = max((len(longest_value), len(col_name)))

        header = " | ".join(
            f"{col_name:<{column_widths[col_name]}}" for col_name in columns.keys()
        )
        separator = " + ".join("-" * i for i in column_widths.values())

        body = ""
        for server in servers:
            entries = []
            for col_name, col_key in columns.items():
                value = server.get(col_key, "unknown")

                entries.append(f"{value:<{column_widths[col_name]}}")

            body += f"{' | '.join(entries)}\n"

        await ctx.send(f"```\n{header}\n{separator}\n{body}```")


def setup(bot: Bot) -> None:
    bot.add_cog(UnityStation(bot))
