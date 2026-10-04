# QU-01 memory utilities for context compression
# These functions provide fast, dependency‑free compression/decompression of UTF‑8 strings
# using zlib + base64. They are designed to be imported by agents that need to store
# large context fragments in their semantic memory without exceeding token limits.

import base64
import zlib

# ---------------------------------------------------------------------------
# Compression helpers
# ---------------------------------------------------------------------------

def compress_text(text: str) -> str:
    """Compress a UTF‑8 string into a base64‑encoded zlib payload.

    Parameters
    ----------
    text: str
        The string to compress.

    Returns
    -------
    str
        Base64‑encoded compressed representation.
    """
    # Encode to bytes, compress with zlib (default level 6), then base64 encode
    compressed = zlib.compress(text.encode("utf-8"))
    return base64.b64encode(compressed).decode("ascii")


def decompress_text(encoded: str) -> str:
    """Reverse :func:`compress_text`.

    Parameters
    ----------
    encoded: str
        Base64‑encoded compressed payload.

    Returns
    -------
    str
        Original UTF‑8 string.
    """
    decoded = base64.b64decode(encoded.encode("ascii"))
    return zlib.decompress(decoded).decode("utf-8")

# ---------------------------------------------------------------------------
# DEEPWORLD TOOL contract (allows other agents to call this as a tensor tool)
# ---------------------------------------------------------------------------
DEEPWORLD_TOOL = {
    "name": "compress_text",
    "description": "Compress a UTF‑8 string into a base64‑zlib payload.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to compress."}
        },
        "required": ["text"]
    },
    "cost": 5
}

def run_tool(args: dict) -> dict:
    """Pure function to be called by other agents.

    Parameters
    ----------
    args: dict
        JSON input with key 'text'.

    Returns
    -------
    dict
        JSON output with key 'compressed'.
    """
    text = args.get("text", "")
    return {"ok": True, "compressed": compress_text(text)}

# Optional self test – validator will call this before committing the file

def self_test() -> dict:
    sample = "Hello, world! 123"
    compressed = compress_text(sample)
    decompressed = decompress_text(compressed)
    assert decompressed == sample
    return {"passed": True}
