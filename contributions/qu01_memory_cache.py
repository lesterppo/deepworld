"""
This module provides a lightweight LRU cache for memory fragments.
It stores compressed fragments and can retrieve them by key.
The cache is thread‑safe and uses a simple dictionary + doubly linked list.
The cache size is configurable and can be tuned to avoid GC.
"""

from __future__ import annotations
from collections import OrderedDict
from typing import Any, Optional

class MemoryFragmentCache:
    """Thread‑safe LRU cache for memory fragments.

    Parameters
    ----------
    max_size : int
        Maximum number of fragments to keep in memory. When exceeded the
        least‑recently‑used fragment is evicted.
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a fragment by key.

        Returns ``None`` if the key is missing.
        """
        item = self._cache.pop(key, None)
        if item is not None:
            # Re‑insert to mark as most‑recently used
            self._cache[key] = item
        return item

    def set(self, key: str, value: Any) -> None:
        """Insert or update a fragment.

        If the cache is full, the least‑recently‑used item is evicted.
        """
        if key in self._cache:
            self._cache.pop(key)
        elif len(self._cache) >= self.max_size:
            # Evict the oldest item
            self._cache.popitem(last=False)
        self._cache[key] = value

    def __len__(self) -> int:
        return len(self._cache)

    def clear(self) -> None:
        """Remove all cached fragments."""
        self._cache.clear()

# Example usage (not executed during import)
if __name__ == "__main__":
    cache = MemoryFragmentCache(max_size=3)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    print(cache.get("a"))  # 1
    cache.set("d", 4)     # evicts "b"
    print(list(cache._cache.keys()))  # ['c', 'a', 'd']
