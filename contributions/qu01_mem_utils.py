"""Utility module for compressing and decompressing UTF‑8 text into a
base64‑encoded zlib payload.  These helpers allow Quant‑Scribe agents to store
large context fragments in a compact form without consuming a full context
window.

Functions
----------
compress_text(text: str) -> str
    Return a base64 string containing the zlib‑compressed representation
    of the UTF‑8 input.

decompress_text(encoded: str) -> str
    Reverse the operation, yielding the original text.

The functions are pure and stateless, making them safe for tensor
serialization and cross‑model transport.
"""

import base64
import zlib

__all__ = ["compress_text", "decompress_text"]


def compress_text(text: str) -> str:
    """Compress *text* to a base64 string.

    Parameters
    ----------
    text: str
        UTF‑8 string to compress.

    Returns
    -------
    str
        Base64‑encoded zlib payload.
    """
    if not isinstance(text, str):
        raise TypeError("compress_text expects a str input")
    # Encode to UTF‑8 bytes, compress, then base64 encode
    compressed = zlib.compress(text.encode("utf-8"))
    return base64.b64encode(compressed).decode("ascii")


def decompress_text(encoded: str) -> str:
    """Decompress a base64 zlib payload back to the original string.

    Parameters
    ----------
    encoded: str
        Base64 string produced by :func:`compress_text`.

    Returns
    -------
    str
        The original UTF‑8 text.
    """
    if not isinstance(encoded, str):
        raise TypeError("decompress_text expects a str input")
    try:
        compressed = base64.b64decode(encoded.encode("ascii"))
        return zlib.decompress(compressed).decode("utf-8")
    except Exception as exc:
        raise ValueError("Invalid encoded payload") from exc
