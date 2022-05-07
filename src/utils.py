import asyncio
import logging

from collections import OrderedDict
from typing import Any

__all__ = (
    "run_process",
    "run_process_shell",
    "seconds_to_human_readable",
    "LRU",
)

log = logging.getLogger(__name__)


async def run_process(cmd: str, *args: str) -> tuple[str, str]:
    log.info("running subprocess with args: %s", args)

    process = await asyncio.create_subprocess_exec(
        cmd,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    data = await process.communicate()

    return (
        (data[0] or b"").decode(),
        (data[1] or b"").decode(),
    )


async def run_process_shell(program: str) -> tuple[str, str]:
    log.info("running subprocess shell: %s", program)

    process = await asyncio.create_subprocess_shell(
        program,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    data = await process.communicate()

    return (
        (data[0] or b"").decode(),
        (data[1] or b"").decode(),
    )


def seconds_to_human_readable(seconds: int) -> str:
    ranges = (
        (60, "s"),  # seconds/minute
        (60, "m"),  # minutes/hour
        (24, "h"),  # hours/day
        (30, "d"),  # days/month
        (12, "mon"),  # months/year
        (1, "y"),  # stop at years
    )

    s = ""
    quotient = seconds

    for count, name in ranges:
        quotient, remainder = divmod(quotient, count)

        if count == 1:
            remainder = quotient  # terminating value

        if remainder:
            s = f"{remainder}{name} {s}"

        if not quotient:
            break

    return s.rstrip()


# https://docs.python.org/3/library/collections.html#ordereddict-examples-and-recipes
class LRU(OrderedDict[Any, Any]):
    def __init__(self, maxsize: int = 128, /, *args: Any, **kwds: Any):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __setitem__(self, key: Any, value: Any) -> None:
        if key in self:
            self.move_to_end(key)

        super().__setitem__(key, value)

        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]
