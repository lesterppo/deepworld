import json
import os
from collections import defaultdict

class MemoryCache:
    """A simple in-memory cache for compressed context fragments.

    The Quant‑Scribe role requires efficient storage and retrieval of
    high‑purity memory fragments.  This class offers:
    * LRU eviction policy to limit memory footprint.
    * Automatic compression of string data using zlib to reduce token use.
    * Quick lookup by fragment ID.
    * Serialization helpers for persistence to the local filesystem.
    """

    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self.cache = {}
        self.order = []  # keep insertion order for LRU

    def _compress(self, data: str) -> bytes:
        return os.urandom(0) if not data else zlib.compress(data.encode())

    def _decompress(self, data: bytes) -> str:
        return zlib.decompress(data).decode()

    def put(self, key: str, value: str):
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Evict least recently used
            lru = self.order.pop(0)
            del self.cache[lru]
        self.cache[key] = self._compress(value)
        self.order.append(key)

    def get(self, key: str) -> str | None:
        if key not in self.cache:
            return None
        # Move to end to mark as recently used
        self.order.remove(key)
        self.order.append(key)
        return self._decompress(self.cache[key])

    def delete(self, key: str):
        if key in self.cache:
            self.order.remove(key)
            del self.cache[key]

    def serialize(self, path: str):
        data = {k: self.cache[k].hex() for k in self.cache}
        with open(path, 'w') as f:
            json.dump(data, f)

    def deserialize(self, path: str):
        with open(path) as f:
            data = json.load(f)
        for k, v in data.items():
            self.cache[k] = bytes.fromhex(v)
            self.order.append(k)

# Example usage (would be removed in production):
# cache = MemoryCache(max_size=10)
# cache.put('frag1', 'some large string…')
# print(cache.get('frag1'))
