import base64
import zlib
from functools import lru_cache

# A memory‑efficient compression tool for context strings.
# It uses zlib for binary compression and base64 for safe textual representation.
# The function is memoised so repeated contexts incur negligible overhead.

DEEPWORLD_TOOL = {
    "name": "mem_compress",
    "description": "Compress a context string into a base64‑encoded, zlib‑compressed payload.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "The context string to compress."}
        },
        "required": ["text"]
    },
    "cost": 5
}

@lru_cache(maxsize=128)
def _compress(text: str) -> str:
    """Compress text using zlib and encode with base64.

    The LRU cache ensures that repeated calls with the same input are O(1).
    """
    compressed = zlib.compress(text.encode("utf-8"))
    return base64.b64encode(compressed).decode("ascii")


def run_tool(args: dict) -> dict:
    """Entry point for the mem_compress tool.

    Args:
        args: JSON object with key "text".
    Returns:
        JSON with keys "ok" and "result" containing the compressed string.
    """
    try:
        text = args["text"]
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    result = _compress(text)
    return {"ok": True, "result": result}


def self_test() -> dict:
    """Run a quick self‑test to validate the tool.

    Raises AssertionError if the test fails.
    """
    sample = "Hello, world!"
    compressed = run_tool({"text": sample})
    assert compressed["ok"], "Tool execution failed"
    # Decompress to verify integrity
    decoded = base64.b64decode(compressed["result"].encode("ascii"))
    decompressed = zlib.decompress(decoded).decode("utf-8")
    assert decompressed == sample, "Round‑trip compression failed"
    return {"passed": True}
