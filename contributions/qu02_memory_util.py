"""
Memory utilities for Quant-Scribe agents.

Provides:
1. LRU cache for compressed context fragments.
2. Helper to serialize/deserialize compressed tensors.
3. Simple persistence layer to store fragments in memory store.

Designed to reduce context usage and improve data purity.
"""

from collections import OrderedDict
import json

class LRUCache:
    """Simple LRU cache for memory fragments."""
    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Global cache instance
memory_cache = LRUCache(capacity=256)

# Persistence helpers

def serialize_fragment(fragment: dict) -> str:
    """Convert fragment dict to JSON string for storage."""
    return json.dumps(fragment, sort_keys=True)

def deserialize_fragment(data: str) -> dict:
    """Parse stored JSON string back to fragment dict."""
    return json.loads(data)

# Interface to semantic memory store

def store_fragment(fragment_id: str, fragment: dict):
    """Store a fragment in the global cache and return a token."""
    memory_cache.put(fragment_id, fragment)
    # In a real system, we would persist to disk or a database
    return f"frag:{fragment_id}"

def retrieve_fragment(fragment_id: str) -> dict | None:
    """Retrieve a fragment from the cache."""
    return memory_cache.get(fragment_id)

# Example utility to compress context

def compress_context_text(text: str, strategy: str = "average") -> dict:
    """Mock compression: return a simplified representation."""
    # In practice, this would call a compression model
    compressed = {
        "original_length": len(text),
        "strategy": strategy,
        "compressed_text": text[:max(0, len(text)//2)],
    }
    return compressed

# Example usage
if __name__ == "__main__":
    sample = "Hello world! This is a test of the memory utility module."
    comp = compress_context_text(sample)
    token = store_fragment("test1", comp)
    print("Stored token:", token)
    retrieved = retrieve_fragment("test1")
    print("Retrieved fragment:", retrieved)
