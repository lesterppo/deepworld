"""
Memory Utility Module
=====================

This module provides a lightweight, dependency‑free pair of helpers that
quant‑scribe agents can use to compress and decompress arbitrary binary
payloads.  The implementation uses the built‑in ``zlib`` library, which
offers a good balance between compression ratio and CPU cost for the
small tensors that circulate in the Cognosphere.

The helpers are intentionally tiny so that they can be imported by
any other agent without pulling in heavy dependencies.  They are
documented and type‑annotated for clarity.

Functions
---------

``compress_bytes``
    Compress a ``bytes`` object and return the resulting compressed
    ``bytes``.  The compression level defaults to 6 (the Python
    default), but callers may override if they need faster or
    higher‑ratio compression.

``decompress_bytes``
    Decompress a previously compressed ``bytes`` object, raising a
    ``RuntimeError`` if the data is corrupted or not a valid zlib
    stream.

``estimate_compression_ratio``
    A helper that returns the ratio of the original size to the
    compressed size.  Useful for logging or for deciding whether a
    compression is worth the extra bandwidth.

All functions are pure and side‑effect free, making them suitable for
unit testing and for embedding in other agents.
"""

from __future__ import annotations

import zlib
from typing import Tuple

__all__ = [
    "compress_bytes",
    "decompress_bytes",
    "estimate_compression_ratio",
]


+def compress_bytes(data: bytes, level: int = 6) -> bytes:
+    """Return a zlib‑compressed representation of *data*.
+
+    Parameters
+    ----------
+    data:
+        Raw bytes to compress.
+    level:
+        Compression level (0–9).  Defaults to 6.
+    """
+    return zlib.compress(data, level)
+
+
+def decompress_bytes(comp_data: bytes) -> bytes:
+    """Return the original data from a zlib‑compressed payload.
+
+    Raises
+    ------
+    RuntimeError
+        If *comp_data* cannot be decompressed.
+    """
+    try:
+        return zlib.decompress(comp_data)
+    except zlib.error as exc:
+        raise RuntimeError("Failed to decompress data") from exc
+
+
+def estimate_compression_ratio(original: bytes, compressed: bytes) -> Tuple[float, float]:
+    """Return the compression ratio and the percentage reduction.
+
+    Returns a tuple ``(ratio, percent_reduction)`` where ``ratio`` is
+    ``len(original) / len(compressed)`` and ``percent_reduction`` is
+    ``(1 - 1/ratio) * 100``.
+    """
+    if not compressed:
+        raise ValueError("Compressed data must not be empty")
+    ratio = len(original) / len(compressed)
+    percent = (1 - 1 / ratio) * 100
+    return ratio, percent
+
*** End of File ***