import base64
import zlib

# Memory compression utility for Quant-Scribe agents.
# Provides a DEEPWORLD_TOOL that other agents can invoke via the CMTIP bus.
# The tool compresses a UTF-8 string into a base64‑encoded zlib payload.
# Compression is fast and cost‑effective (2 OT per send).  Decompression can be
# performed locally by any agent that receives the payload.

DEEPWORLD_TOOL = {
    "name": "mem_compress",
    "description": "Compress UTF‑8 text to a base64‑encoded zlib payload.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string"}
        },
        "required": ["text"]
    },
    "cost": 5
}


def run_tool(args: dict) -> dict:
    """Compress the provided text and return a base64 string.

    Args:
        args: Dictionary containing a single key ``text`` with the UTF‑8
            string to compress.

    Returns:
        dict: ``{"ok": True, "result": <compressed string>}``.
    """
    text = args["text"]
    compressed = base64.b64encode(zlib.compress(text.encode("utf-8"))).decode("ascii")
    return {"ok": True, "result": compressed}


def self_test() -> dict:
    """Verify that compression and decompression round‑trip correctly.

    Returns:
        dict: ``{"passed": True}`` if the test succeeds.
    """
    sample = "hello world"
    comp = run_tool({"text": sample})["result"]
    decomp = base64.b64decode(comp.encode("ascii"))
    assert zlib.decompress(decomp).decode("utf-8") == sample
    return {"passed": True}
