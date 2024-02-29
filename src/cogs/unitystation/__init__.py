from datetime import date
from typing import Any, Optional

from discord.ext import commands

from src.bot import PINK
from src.cog import Cog
from src.context import Context

from .servers import ServerListClient

# avoid invite scraping
US_INVITE = "tFcTpBp"


class UnityStation(Cog):
    # f-strings and .format do not count as docstring
    __doc__ = f"""
    UnityStation related commands

    UnityStation is a SS13 remake in Unity.
    You can learn more about this game by joining their official server: discord.gg/{US_INVITE}
    """

    def cog_check(self, ctx: Context) -> bool:  # type: ignore
        # hide from help but otherwise let users call it. direct help still works because it has extra argument
        if ctx.invoked_with == "help":
            return ctx.guild and ctx.guild.id == 273774715741667329  # type: ignore

        return True

    async def cog_load(self) -> None:
        self._server_list = ServerListClient()

    @commands.command(aliases=["list", "sv", "ls"])
    async def servers(self, ctx: Context, *, server: Optional[str] = None) -> None:
        """List hub servers"""

        async with ctx.typing():
            await self._server_list.fetch(ctx)

            if server is None:
                text = await self._servers(ctx)
            else:
                text = await self._server(server)

        if text is not None:
            await ctx.send(text)

    async def _server(self, server_name: str) -> str:
        server_name = server_name.lower()

        servers = self._server_list.servers

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
            "password",
            "fps",
            "address",
        )
        longest_name = len(max(fields, key=len))

        main_info = "\n".join(f"{field:<{longest_name}} : {getattr(server, field)}" for field in fields)

        return f"```\n{main_info}\n\nDownloads\n{downloads}```"

    async def _servers(self, ctx: Context) -> Optional[str]:
        servers = self._server_list.servers

        if not servers:
            return "No servers online"

        data = [
            ["name", "build", f"pop [{sum(s.players for s in servers)}]"],
        ]
        table_attributes = ("name", "version", "players")
        for server in servers:
            row = []
            for attribute in table_attributes:
                value = str(getattr(server, attribute))

                if attribute == "version":
                    # mark servers with bad downloads
                    if not server.downloads_good:
                        value = f"{value} !"
                elif attribute == "players":  # noqa: SIM102
                    if server.password:
                        value = f"{value} [#]"

                row.append(value)
            data.append(row)

        # this section applies accents to data to not break table alignment
        # accents only work in guilds
        if ctx.guild is None or (accent_cog := ctx.bot.get_cog("Accents")) is None:

            def apply_accent(s: str) -> str:
                return s
        else:

            def apply_accent(s: str) -> str:
                return accent_cog.apply_member_accents_to_text(member=ctx.me, text=s)  # type: ignore[attr-defined]

        data = [[apply_accent(s) for s in row] for row in data]

        column_widths: dict[int, int] = {}

        for row in data:
            for i, value in enumerate(row):
                column_widths[i] = max(len(value), column_widths.get(i, 0))

        header = " | ".join(
            f"{col_name:<{col_width}}" for col_name, col_width in zip(data[0], column_widths.values(), strict=True)
        )
        separator = " + ".join("-" * i for i in column_widths.values())

        body = ""

        for row in data[1:]:
            values = []
            for i, value in enumerate(row):
                values.append(f"{value:<{column_widths[i]}}")

            body += f"{' | '.join(values)}\n"

        await ctx.send(f"```\n{header}\n{separator}\n{body}```", accents=[])

        return None

    @commands.command(aliases=["cl"])
    async def changelog(self, ctx: Context, *, build: Optional[str] = None) -> None:
        """Unitystation changelog"""

        if build is not None:
            async with ctx.session.get(f"https://changelog.unitystation.org/changes/{build}") as r:
                changes: list[dict[str, Any]] = await r.json()

        else:
            async with ctx.session.get("https://changelog.unitystation.org/whats-new") as r:
                data = await r.json()
                build = data["build"]
                changes = data["changes"]

        if not changes:
            await ctx.reply(f"No changes in build **{build}** or it does not exist at all idk")

            return

        longest_category = len(max(changes, key=lambda x: len(x["category"]))["category"])

        sorted_changes = sorted(
            changes,
            # priorities: is new, is fix, every other tag else alphabetically, date, pr number from new to old, author
            # name
            # NOTE: this is a mess and is probably borken
            key=lambda c: (
                c["category"].lower() != "new",
                c["category"].lower() != "fix",
                c["category"],
                date.fromisoformat(c["date_added"]),
                c["pr_number"],
                c["author_username"],
            ),
        )

        changes_joined = ""

        current_pr = -1
        for change in sorted_changes:
            if (pr := change["pr_number"]) != current_pr:
                current_pr = pr
                changes_joined += f"\n**{pr}** by **{change['author_username']}**"

            if (description := change["description"]).endswith("."):
                # usage of dot is annoyingly inconsistent
                description = description[:-1]

            changes_joined += f"\n`{change['category']:<{longest_category}}` {description}"

        await ctx.send(
            f"""\
build: **{build}**
PR base url: {changes[0]["pr_url"].rsplit("/", 1)[0]}/
{changes_joined}\
""",
            suppress_embeds=True,
        )


async def setup(bot: PINK) -> None:
    await bot.add_cog(UnityStation(bot))
