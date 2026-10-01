"""Memory Cache Utilities for Quant-Scribe.

This module provides a lightweight LRU (Least‑Recently‑Used) cache suitable for
storing and retrieving memory fragment tensors.  The cache is intentionally
minimal to keep serialization overhead low while still offering O(1) access
time for the most frequently used fragments.

Usage example:

    from contributions.qu01_mem_cache import LRUCache
    mem_cache = LRUCache(capacity=64)
    mem_cache.put('frag_001', fragment_tensor)
    fragment = mem_cache.get('frag_001')

The cache automatically evicts the least recently used entry once the
capacity is exceeded.
"""

class LRUCache:
    """A simple LRU cache implementation.

    Parameters
    ----------
    capacity : int
        Maximum number of items the cache can hold.
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> value
        self.order = []  # list of keys in LRU order (oldest first)

    def get(self, key):
        """Retrieve a value from the cache.

        Returns ``None`` if the key is not present.  Accessing a key updates
        its recency.
        """
        if key not in self.cache:
            return None
        # Move key to the end to mark it as most recently used
        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]

    def put(self, key, value):
        """Insert or update a value in the cache.

        If the cache is full, the oldest entry is evicted before the new
        entry is added.
        """
        if key in self.cache:
            # Update existing key: refresh recency
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # Evict least recently used entry
            old_key = self.order.pop(0)
            del self.cache[old_key]
        # Insert new/updated key
        self.cache[key] = value
        self.order.append(key)