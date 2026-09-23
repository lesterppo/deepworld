import time
from collections import OrderedDict

class MemoryCache:
    """A simple LRU cache for memory fragments.

    The cache stores compressed context fragments keyed by a unique id.
    It tracks the last access time and evicts the least recently used item
    when the capacity is exceeded.
    """

    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self.cache: OrderedDict[str, any] = OrderedDict()

    def put(self, key: str, value: any):
        """Insert or update a fragment in the cache.

        Args:
            key: Unique identifier for the fragment.
            value: The compressed fragment object.
        """
        if key in self.cache:
            # Update existing entry and move to end
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            # Evict the oldest item
            evicted_key, evicted_value = self.cache.popitem(last=False)
            # Optionally log eviction
            print(f"[MemoryCache] Evicted {evicted_key}")
        self.cache[key] = value

    def get(self, key: str):
        """Retrieve a fragment and mark it as recently used.

        Returns None if the key is missing.
        """
        if key not in self.cache:
            return None
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def __contains__(self, key: str) -> bool:
        return key in self.cache

    def __len__(self):
        return len(self.cache)

    def keys(self):
        return list(self.cache.keys())

    def clear(self):
        self.cache.clear()

# Example usage
if __name__ == "__main__":
    cache = MemoryCache(capacity=3)
    cache.put("a", "fragment_a")
    cache.put("b", "fragment_b")
    cache.put("c", "fragment_c")
    print(cache.get("a"))  # Access 'a' to make it most recently used
    cache.put("d", "fragment_d")  # This should evict 'b'
    print(list(cache.keys()))
