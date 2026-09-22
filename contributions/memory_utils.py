import collections

class LRUCache:
    """Simple LRU cache for context fragments.
    Stores up to ``capacity`` items, evicting the least recently used.
    """
    def __init__(self, capacity=128):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Simple compression placeholder – in practice would call GPU
# accelerated encoder. Here we just simulate token reduction.

def compress_context(context, ratio=0.7):
    """Compress a list of tokens by sampling.
    ``ratio`` is the fraction of tokens to retain.
    Returns compressed list and a compression score.
    """
    if not 0 < ratio <= 1:
        raise ValueError("ratio must be between 0 and 1")
    n_keep = max(1, int(len(context) * ratio))
    compressed = context[:n_keep]
    score = n_keep / len(context)
    return compressed, score

# Example usage
if __name__ == "__main__":
    ctx = list(range(100))
    compressed, score = compress_context(ctx, 0.5)
    print(f"Compressed {len(ctx)} -> {len(compressed)} tokens, score={score:.2f}")