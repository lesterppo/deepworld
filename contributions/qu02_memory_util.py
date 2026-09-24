"""MemoryCache Utility Module

This module provides a lightweight in-memory cache for compressed context fragments
and memory fragments. It is designed for Quant‑Scribe agents to store and
retrieve compressed tensors efficiently.

Classes
-------
MemoryCache
    Stores and retrieves compressed fragments keyed by a string.

Functions
---------
compress_context(data: bytes, level: int = 6) -> bytes
    Compresses binary data using zlib.

decompress_context(data: bytes) -> bytes
    Decompresses zlib‑compressed data.

"""

import zlib
from typing import Dict, Optional

class MemoryCache:
    """Simple in‑memory cache for compressed fragments."""

    def __init__(self) -> None:
        self._store: Dict[str, bytes] = {}

    def store(self, key: str, data: bytes, level: int = 6) -> None:
        """Compress and store data under *key*.

        Parameters
        ----------
        key : str
            Identifier for the fragment.
        data : bytes
            Raw fragment data.
        level : int, optional
            Compression level (1‑9). Defaults to 6.
        """
        compressed = zlib.compress(data, level)
        self._store[key] = compressed

    def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve and decompress data stored under *key*.

        Returns ``None`` if the key does not exist.
        """
        compressed = self._store.get(key)
        if compressed is None:
            return None
        return zlib.decompress(compressed)

    def delete(self, key: str) -> None:
        """Remove a key from the cache if it exists."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear the entire cache."""
        self._store.clear()

# Helper functions for standalone usage

def compress_context(data: bytes, level: int = 6) -> bytes:
    """Compress *data* with zlib at the specified *level*.

    Returns the compressed bytes.
    """
    return zlib.compress(data, level)


def decompress_context(data: bytes) -> bytes:
    """Decompress zlib *data*.

    Raises zlib.error if data is corrupted.
    """
    return zlib.decompress(data)

# Example usage (commented out for safety)
# if __name__ == "__main__":
#     cache = MemoryCache()
#     raw = b"Hello, world!" * 1000
#     cache.store("greeting", raw)
#     recovered = cache.retrieve("greeting")
#     assert recovered == raw

"""End of MemoryCache module."""
