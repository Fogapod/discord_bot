from __future__ import annotations

import inspect

from functools import partial, update_wrapper, wraps
from typing import Any, Callable, Coroutine, Dict, Iterable, List, Optional, ParamSpec, TypeVar

__all__ = (
    "HookHost",
    "Hookable",
)

T = TypeVar("T")
P = ParamSpec("P")

Coro = Coroutine[Any, Any, T]

# TODO: Protocol
_HookType = Callable[..., Coro[Any]]


class HookHost:
    """Enables hooks to be defined in class"""

    __slots__ = ("__active_hooks__",)

    __active_hooks__: List[_HookType]

    def __new__(cls, *args: Any, **kwargs: Any) -> HookHost:
        self = super().__new__(cls, *args, **kwargs)

        hooks = []

        for base in cls.__mro__:
            for value in base.__dict__.values():
                if inspect.iscoroutinefunction(value):
                    if hasattr(value, "__hook_target__"):
                        value.__hook_self_instance__ = self
                        hooks.append(value)

        self.__active_hooks__ = hooks

        return self

    def release_hooks(self) -> None:
        for hook in self.__active_hooks__:
            hook.__hook_target__.remove_hook(hook)  # type: ignore[attr-defined]

        self.__active_hooks__ = []


class Hookable:
    """
    Allows for type method intercepting, similar to aiohttp middlewares. Currently only works with custom Cog class
    because of the way self argument is injected.
    """

    __hooks__: Dict[str, List[_HookType]] = {}

    def _hooks_for(self, name: str) -> Iterable[_HookType]:
        return self.__hooks__.get(name, ())

    # mypy does not seem to understand wrapping decorator. any attempt to use ParamSpec resulted in function losing its
    # arguments or locking it to first decorated signture preventing from using @hookable for other functions
    @classmethod
    def hookable(cls) -> Any:
        """Make method hookable"""

        # TODO: Concatenate[Any, P] for self arg once mypy supports it
        def decorator(func: Callable[P, Coro[T]]) -> Callable[P, Coro[T]]:
            name = func.__name__

            @wraps(func)
            def wrapped(self: Any, *args: P.args, **kwargs: P.kwargs) -> Coro[T]:
                handler: _HookType = getattr(self, name).__original__

                # thanks aiohttp
                # https://github.com/aio-libs/aiohttp/blob/3edc43c1bb718b01a1fbd67b01937cff9058e437/aiohttp/web_app.py#L346-L350
                for hook in self._hooks_for(name):
                    handler = update_wrapper(partial(hook, hook.__hook_self_instance__, handler), handler)

                return handler(self, *args, **kwargs)

            wrapped.__original__ = func  # type: ignore[attr-defined]

            return wrapped  # type: ignore

        return decorator

    @classmethod
    def hook(cls, name: Optional[str] = None) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Makes decorated method a hook for given method of original hookable"""

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Not a coroutine")

            nonlocal name

            if name is None:
                if (name := func.__name__).startswith("on_"):
                    name = name[3:]

            original = getattr(cls, name, None)
            if original is None:
                raise ValueError(f"Function does not exist: {name}")

            if not hasattr(original, "__original__"):
                raise ValueError(f"Function is not hookable: {name}")

            func.__hook_name__ = name  # type: ignore[attr-defined]
            func.__hook_target__ = cls  # type: ignore[attr-defined]

            cls.__hooks__.setdefault(name, [])
            cls.__hooks__[name].append(func)  # type: ignore[arg-type]

            return func

        return decorator

    @classmethod
    def remove_hook(cls, hook: _HookType) -> None:
        name = hook.__hook_name__  # type: ignore[attr-defined]
        if name in cls.__hooks__:
            try:
                cls.__hooks__[name].remove(hook)
            except ValueError:
                pass
