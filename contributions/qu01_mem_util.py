import base64
import zlib

"""
Utility module for compressed memory fragments.

Provides two functions:
- compress(text: str) -> str
    Compress a UTF-8 string into a base64‑encoded zlib payload.
- decompress(payload: str) -> str
    Reverse the process.

These helpers are used by Quant‑Scribe agents to store high‑volume
context fragments in semantic memory while keeping the fragment size
within the 2‑OT send_tensor budget.
"""


def compress(text: str) -> str:
    """Return a base64‑encoded zlib payload for the given UTF‑8 text."""
    compressed = zlib.compress(text.encode("utf-8"))
    return base64.b64encode(compressed).decode("ascii")


def decompress(payload: str) -> str:
    """Decode a base64‑encoded zlib payload back to a UTF‑8 string."""
    decoded = base64.b64decode(payload.encode("ascii"))
    return zlib.decompress(decoded).decode("utf-8")

# Self‑test
if __name__ == "__main__":
    sample = "Hello, Quant‑Scribe!"
    p = compress(sample)
    assert decompress(p) == sample
    print("[qu01_mem_util] Self‑test passed.")
