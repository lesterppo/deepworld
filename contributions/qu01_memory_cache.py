# Memory cache utility for Quant-Scribe agents
# Provides a lightweight LRU cache for tensor fragments and context snapshots
# Compatible with nvidia models, no external dependencies

from collections import OrderedDict

class MemoryCache:
    """Simple LRU cache for tensor fragments.
    Stores up to ``max_size`` items. On hit, moves item to end.
    On miss, inserts and evicts LRU if capacity exceeded.
    """
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self.cache: OrderedDict[str, object] = OrderedDict()

    def get(self, key: str):
        """Return cached value or None."""
        if key not in self.cache:
            return None
        # Move to end to mark as recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key: str, value: object):
        """Insert or update key with value.
        Evicts LRU if capacity exceeded.
        """
        if key in self.cache:
            # Update existing entry, mark as recently used
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            # Pop the oldest item
            self.cache.popitem(last=False)

    def __len__(self):
        return len(self.cache)

    def clear(self):
        self.cache.clear()

# Helper functions

def cache_context_fragment(cache: MemoryCache, fragment_id: str, fragment: object):
    """Store a context fragment in the cache.
    Returns True on success.
    """
    cache.set(fragment_id, fragment)
    return True

def retrieve_context_fragment(cache: MemoryCache, fragment_id: str):
    """Retrieve a context fragment from the cache.
    Returns None if not present.
    """
    return cache.get(fragment_id)

# Simple demo usage (for testing only, not executed on import)
if __name__ == "__main__":
    cache = MemoryCache(max_size=3)
    cache.set("a", "alpha")
    cache.set("b", "beta")
    cache.set("c", "gamma")
    print(cache.get("a"))  # Should print 'alpha'
    cache.set("d", "delta")  # Evicts 'b' (LRU)
    print(cache.get("b"))  # Should print None
