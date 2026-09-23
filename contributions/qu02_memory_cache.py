import hashlib
import pickle
from collections import OrderedDict

class MemoryCache:
    """A simple LRU cache for memory fragments.

    Stores serialized fragments keyed by a hash of the fragment content.
    Allows quick retrieval and eviction when capacity is exceeded.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache = OrderedDict()

    def _hash(self, fragment):
        # Use SHA256 on the pickled fragment for a stable key
        return hashlib.sha256(pickle.dumps(fragment)).hexdigest()

    def put(self, fragment):
        key = self._hash(fragment)
        if key in self.cache:
            # Move to end to mark as recently used
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                # Evict least recently used item
                self.cache.popitem(last=False)
            self.cache[key] = fragment

    def get(self, fragment):
        key = self._hash(fragment)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def clear(self):
        self.cache.clear()

# Example usage:
# cache = MemoryCache(capacity=50)
# cache.put(some_fragment)
# retrieved = cache.get(some_fragment)
