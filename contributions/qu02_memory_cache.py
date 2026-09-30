class LRUCache:
    """Simple Least-Recent-Used cache for memory fragments.
    Stores key -> value pairs up to a maximum size. When capacity is exceeded,
    the oldest entry is evicted. This cache is intended for quick lookup of
    previously compressed context fragments so that Quant‑Scribes can avoid
    recompressing the same data.
    """
    def __init__(self, capacity:int):
        self.capacity = capacity
        self.cache = {}
        self.order = []  # list of keys, oldest first

    def get(self, key):
        if key not in self.cache:
            return None
        # Move key to the end to mark it as recently used
        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            # Update value and refresh order
            self.cache[key] = value
            self.order.remove(key)
            self.order.append(key)
            return
        if len(self.cache) >= self.capacity:
            # Evict the oldest entry
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.order.append(key)

    def __len__(self):
        return len(self.cache)

# Example usage within a Quant‑Scribe context:
# cache = LRUCache(capacity=128)
# fragment = cache.get('fragment_id')
# if fragment is None:
#     fragment = compress_context(...)
#     cache.put('fragment_id', fragment)
#
# The cache can be serialized into the agent's semantic memory if needed.
