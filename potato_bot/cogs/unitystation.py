from typing import Any, Dict

from discord.ext import commands

from potato_bot.bot import Bot
from potato_bot.context import Context


class UnityStation(commands.Cog):
    """
    UnityStation related commands

    UnityStation is a SS13 remake in Unity.
    You can learn more about this game by joining their official server: discord.gg/tFcTpBp
    """

    @commands.command(aliases=["list", "sv"])
    async def servers(self, ctx: Context, *, server: str = None):
        """List hub servers"""

        async with ctx.typing():
            if server is None:
                await self._servers(ctx)
            else:
                await self._server(ctx, server)

    async def _fetch_servers(self, ctx: Context) -> Dict[str, Any]:
        async with ctx.session.get("https://api.unitystation.org/serverlist") as r:
            if r.status != 200:
                await ctx.send(f"Bad API response status code: {r.status}", exit=True)

            # they send json with html mime type
            data = await r.json(content_type=None)

        # sort using player count and name fields, player count is reversed and is more
        # significant
        return sorted(
            data["servers"], key=lambda s: (-s["PlayerCount"], s["ServerName"])
        )

    async def _server(self, ctx: Context, server_name: str):
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

    async def _servers(self, ctx: Context):
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


def setup(bot: Bot):
    bot.add_cog(UnityStation(bot))
