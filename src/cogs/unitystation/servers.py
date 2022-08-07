from __future__ import annotations

import asyncio
import collections
import logging
import time

from dataclasses import InitVar, dataclass, field
from typing import Any, ClassVar, List, Mapping

import aiohttp

from aiocache import SimpleMemoryCache

from src.classes.context import Context
from src.errors import PINKError

log = logging.getLogger(__name__)


DownloadAddressResponse = collections.namedtuple("DownloadAddressResponse", ["status", "error"])


class DownloadAddress:
    _cache: ClassVar[SimpleMemoryCache] = SimpleMemoryCache(ttl=60)
    _locks: ClassVar[SimpleMemoryCache] = SimpleMemoryCache(ttl=60)
    _locks_lock = asyncio.Lock()

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

        self.response = DownloadAddressResponse(0, "not fetched")

    async def check(self, ctx: Context) -> None:
        # cached by earlier requests
        if response := await self._cache.get(self.url):
            self.response = response

            return

        # not in cache - try to be the only one to fetch this url
        async with self._locks_lock:
            if fut := await self._locks.get(self.url):
                # we are not first, just wait for response
                self.response = await fut
                return
            else:
                # we are first, lock url
                fut = asyncio.Future()
                await self._locks.add(self.url, fut)

        try:
            async with ctx.session.head(self.url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                response = DownloadAddressResponse(r.status, None)
        except Exception as e:
            log.error("fetching %r: %s: %s", self, type(e).__name__, str(e))

            response = DownloadAddressResponse(-1, type(e).__name__)

        self.response = response

        fut.set_result(response)

        await self._cache.set(self.url, response)

    @property
    def ok(self) -> bool:
        return self.response.status == 200

    def __str__(self) -> str:
        if self.ok:
            return self.url

        if self.response.error is not None:
            return f"[{self.response.status}] ({self.response.error}) {self.url}"

        return f"[{self.response.status}] {self.url}"

    def __repr__(self) -> str:
        return f"<{type(self).__name__} url={self.url} response={self.response}>"


# note about initvars
# https://github.com/python/mypy/issues/12877#issuecomment-1141001772
@dataclass
class Server:
    _name: InitVar[str]
    name: str = field(init=False)
    fork: str
    version: str
    map: str
    gamemode: str
    time: str
    _players: InitVar[int]
    players: int = field(init=False)
    fps: int
    ip: str
    port: str
    address: str = field(init=False)
    downloads: List[DownloadAddress]

    def __post_init__(self, _name: str, _players: str) -> None:
        # newlines are allowed in server names
        self.name = _name.replace("\n", " ")

        if _players == "unknown":
            self.players = -1
        else:
            self.players = int(_players)

        self.address = f"{self.ip}:{self.port}"

    @classmethod
    def from_data(cls, data: Mapping[str, Any]) -> Server:
        aliases = {
            "ServerName": "_name",
            "ForkName": "fork",
            "BuildVersion": "version",
            "CurrentMap": "map",
            "GameMode": "gamemode",
            "IngameTime": "time",
            "PlayerCount": "_players",
            "fps": "fps",
            "ServerIP": "ip",
            "ServerPort": "port",
        }

        download_aliases = {
            "WinDownload": "windows",
            "LinuxDownload": "linux",
            "OSXDownload": "osx",
        }

        return cls(
            downloads=[DownloadAddress(v, data[k]) for k, v in download_aliases.items()],
            # how is this an incompatibe type, mypy???
            **{v: str(data.get(k, "unknown")) for k, v in aliases.items()},  # type: ignore
        )

    async def check_downloads(self, ctx: Context) -> None:
        await asyncio.gather(*[d.check(ctx) for d in self.downloads])

    @property
    def downloads_good(self) -> bool:
        return all(d.ok for d in self.downloads)


class ServerList:
    FETCH_INTERVAL = 10

    def __init__(self) -> None:
        self.servers: List[Server] = []
        self._fetch_time = time.monotonic() - self.FETCH_INTERVAL

    async def fetch(self, ctx: Context) -> None:
        if time.monotonic() - self._fetch_time < self.FETCH_INTERVAL:
            return

        async with ctx.session.get(
            "https://api.unitystation.org/serverlist",
            timeout=aiohttp.ClientTimeout(total=30),
        ) as r:
            if r.status != 200:
                raise PINKError(f"Bad API response status code: **{r.status}**")

            # they send json with html mime type
            data = await r.json(content_type=None)

        self._fetch_time = time.monotonic()

        self.servers = sorted(
            [Server.from_data(s) for s in data["servers"]],
            key=lambda s: (-s.players, s.name),
        )

        await self.check_downloads(ctx)

    async def check_downloads(self, ctx: Context) -> None:
        await asyncio.gather(*[s.check_downloads(ctx) for s in self.servers])
