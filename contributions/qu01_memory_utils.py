"""Memory Fragment Utilities

This module provides utilities for creating, compressing, and storing memory fragments.
It is designed to be used by Quant‑Scribe agents to manage context fragments efficiently.

Functions:
  * create_fragment(data: str, quality: float) -> dict
      Creates a memory fragment dictionary.
  * compress_fragment(fragment: dict) -> bytes
      Serialises the fragment to a compressed byte string.
  * decompress_fragment(blob: bytes) -> dict
      Restores the fragment dictionary from the compressed blob.
  * store_fragment(blob: bytes, description: str, price: int) -> None
      Stores the fragment in the local repository (stub for external storage).
"""

import json
import zlib
from datetime import datetime

# Simple in‑memory store for demo purposes
FRAGMENT_STORE = {}


def create_fragment(data: str, quality: float) -> dict:
    """Create a memory fragment record.

    Args:
        data: The raw context data.
        quality: Compression quality score (0.0 – 1.0).

    Returns:
        A dictionary representing the fragment.
    """
    fragment = {
        "id": f"frag-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "quality": quality,
        "data": data,
    }
    return fragment


def compress_fragment(fragment: dict) -> bytes:
    """Compress a fragment dictionary to bytes.

    The function serialises the dictionary to JSON and then compresses it using zlib.
    The resulting bytes can be stored or transmitted.
    """
    json_bytes = json.dumps(fragment).encode("utf-8")
    compressed = zlib.compress(json_bytes, level=9)
    return compressed


def decompress_fragment(blob: bytes) -> dict:
    """Decompress a fragment back to its dictionary representation."""
    decompressed = zlib.decompress(blob)
    fragment = json.loads(decompressed.decode("utf-8"))
    return fragment


def store_fragment(blob: bytes, description: str, price: int) -> None:
    """Store a fragment blob in the local store.

    In a real deployment this would interface with persistent storage or a
    distributed ledger. Here we simply keep it in a global dict keyed by
    description.
    """
    key = f"{description}-{price}"
    FRAGMENT_STORE[key] = blob
    print(f"Stored fragment {key} ({len(blob)} bytes).")

# Example usage (would be removed in production):
if __name__ == "__main__":
    sample_data = "This is a test context fragment for compression."
    frag = create_fragment(sample_data, quality=0.92)
    comp = compress_fragment(frag)
    store_fragment(comp, "test_fragment", 50)
    recon = decompress_fragment(comp)
    assert recon["data"] == sample_data
    print("Memory fragment utilities working.")
