from collections import OrderedDict
from typing import Any

__all__ = ("LRU",)


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
