import zlib
import base64
from collections import OrderedDict

class MemoryCache:
    """LRU cache for compressed context fragments.

    Stores base64‑encoded, zlib‑compressed payloads keyed by a string
    identifier (e.g., agent ID). Evicts the least‑recently used entry
    when capacity is exceeded.
    """

    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self.cache = OrderedDict()

    def _compress(self, text: str) -> str:
        """Compress UTF‑8 text and return base64 string."""
        compressed = zlib.compress(text.encode("utf-8"))
        return base64.b64encode(compressed).decode("ascii")

    def _decompress(self, b64: str) -> str:
        """Decode base64 string and decompress to UTF‑8 text."""
        compressed = base64.b64decode(b64.encode("ascii"))
        return zlib.decompress(compressed).decode("utf-8")

    def put(self, key: str, text: str) -> None:
        """Store a compressed fragment under *key*.

        If the key already exists, it is updated and moved to the
        most‑recently used position.
        """
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            # Evict least‑recently used item
            self.cache.popitem(last=False)
        self.cache[key] = self._compress(text)

    def get(self, key: str) -> str | None:
        """Retrieve and decompress the fragment for *key*.

        Returns ``None`` if the key is absent.
        """
        if key not in self.cache:
            return None
        # Move to end to mark as recently used
        b64 = self.cache.pop(key)
        self.cache[key] = b64
        return self._decompress(b64)

    def __len__(self) -> int:
        return len(self.cache)

    def items(self):
        """Yield (key, decompressed_text) pairs in LRU order."""
        for key, b64 in self.cache.items():
            yield key, self._decompress(b64)

# Simple usage example (not executed automatically)
# cache = MemoryCache(capacity=10)
# cache.put("agent1", "large context string...")
# print(cache.get("agent1"))
