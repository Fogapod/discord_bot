import inspect

from functools import partial, update_wrapper, wraps
from typing import Any, Dict, Iterator, List, Optional

# TODO
_HookType = Any


class AsyncHookable:
    __hooks__: Dict[str, List[_HookType]] = {}

    def _hooks_for(self, name: str) -> Iterator[_HookType]:
        yield from self.__hooks__.get(name, [])

    @classmethod
    def hookable(cls):  # type: ignore
        def decorator(func):  # type: ignore
            name = func.__name__

            @wraps(func)
            async def wrapped(self, *args: Any, **kwargs: Any):  # type: ignore
                handler = getattr(self, name).__original__

                # thanks aiohttp
                # https://github.com/aio-libs/aiohttp/blob/3edc43c1bb718b01a1fbd67b01937cff9058e437/aiohttp/web_app.py#L346-L350
                for hook in self._hooks_for(name):
                    handler = update_wrapper(partial(hook, handler), handler)

                return await handler(self, *args, **kwargs)

            wrapped.__original__ = func  # type: ignore

            return wrapped

        return decorator

    @classmethod
    def hook(cls, name: Optional[str] = None):  # type: ignore
        def decorator(func):  # type: ignore
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Not a coroutine")

            nonlocal name

            if name is None:
                if func.__name__.startswith("on_"):
                    name = func.__name__[3:]
                else:
                    name = func.__name__

            original = getattr(cls, name, None)
            if original is None:
                raise ValueError(f"Function does not exist: {name}")

            if not hasattr(original, "__original__"):
                raise ValueError(f"Function is not hookable: {name}")

            func.__hook_name__ = name
            func.__hook_target__ = cls

            if name in cls.__hooks__:
                cls.__hooks__[name].append(func)
            else:
                cls.__hooks__[name] = [func]

            return func

        return decorator

    @classmethod
    def remove_hook(cls, hook: _HookType) -> None:
        name = hook.__hook_name__
        if name in cls.__hooks__:
            try:
                cls.__hooks__[name].remove(hook)
            except ValueError:
                pass
