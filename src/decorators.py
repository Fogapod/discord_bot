import asyncio

from collections.abc import Awaitable, Callable
from concurrent.futures import Executor
from functools import partial, wraps
from typing import Optional, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


# NOTE: is there a meaningful way to use executor param? maybe use enum instead
def in_executor(executor: Optional[Executor] = None) -> Callable[[Callable[P, T]], Callable[P, Awaitable[T]]]:
    """Make blocking function non-blocking by running it in a given executor"""

    def inner(fn: Callable[P, T]) -> Callable[P, Awaitable[T]]:
        @wraps(fn)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> Awaitable[T]:
            loop = asyncio.get_running_loop()
            return loop.run_in_executor(executor, partial(fn, *args, **kwargs))

        return wrapped

    return inner
