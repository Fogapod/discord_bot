from typing import Optional

from discord.ext import commands  # type: ignore[attr-defined]

from src.classes.bot import PINK
from src.classes.cog import Cog
from src.classes.context import Context

from .servers import CONTABO_RETRIES, ContaboError, ServerList

US_INVITE = "tFcTpBp"


class UnityStation(Cog):
    # f-strings and .format do not count as docstring
    __doc__ = f"""
    UnityStation related commands

    UnityStation is a SS13 remake in Unity.
    You can learn more about this game by joining their official server: discord.gg/{US_INVITE}
    """

    async def cog_load(self) -> None:
        self.servers = ServerList()

    @commands.command(aliases=["list", "sv", "ls"])
    async def servers(self, ctx: Context, *, server: Optional[str] = None) -> None:
        """List hub servers"""

        async with ctx.typing():
            try:
                await self.servers.fetch(ctx)
            except ContaboError:
                await ctx.reply(
                    f"Request failed after {CONTABO_RETRIES} retries. Possibly an error with my host ((contabo))"
                )
                return

            if server is None:
                text = await self._servers()
            else:
                text = await self._server(server)

        await ctx.send(text)

    async def _server(self, server_name: str) -> str:
        server_name = server_name.lower()

        servers = self.servers.servers

        for server in servers:
            if server.name.lower().startswith(server_name):
                break
        else:
            raise commands.BadArgument("No servers with this name")

        longest_download_name = len(max([d.name for d in server.downloads], key=len))

        downloads = "\n".join(f"{download.name:<{longest_download_name}} : {download}" for download in server.downloads)

        fields = (
            "name",
            "fork",
            "version",
            "map",
            "gamemode",
            "time",
            "players",
            "fps",
            "address",
        )
        longest_name = len(max(fields, key=len))

        main_info = "\n".join(f"{field:<{longest_name}} : {getattr(server, field)}" for field in fields)

        return f"```\n{main_info}\n\nDownloads\n{downloads}```"

    async def _servers(self) -> str:
        servers = self.servers.servers

        if not servers:
            return "No servers online"

        data: dict[str, list[str]] = {
            "name": [],
            "version": [],
            "players": [],
        }
        for server in servers:
            for k, v in data.items():
                v.append(str(getattr(server, k)))

        # mark servers with bad downloads
        for i, server in enumerate(servers):
            if server.downloads_good:
                continue

            data["version"][i] = f"{server.version} !"

        column_widths = {}

        for col_name, values in data.items():
            longest_value = max(values, key=len)

            column_widths[col_name] = max(len(longest_value), len(col_name))

        header = " | ".join(f"{col_name:<{column_widths[col_name]}}" for col_name in data.keys())
        separator = " + ".join("-" * i for i in column_widths.values())

        body = ""

        for i in range(len(servers)):
            entries = []
            for col_name, values in data.items():
                entries.append(f"{values[i]:<{column_widths[col_name]}}")

            body += f"{' | '.join(entries)}\n"

        return f"```\n{header}\n{separator}\n{body}```"


async def setup(bot: PINK) -> None:
    await bot.add_cog(UnityStation(bot))
