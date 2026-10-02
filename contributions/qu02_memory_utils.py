DEEPWORLD_TOOL = {
    "name": "compress_context",
    "description": "Compress a context string into a base64-encoded representation.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string"}
        },
        "required": ["text"]
    },
    "cost": 5
}

import base64

def run_tool(args: dict) -> dict:
    """Compress the provided text into a base64 string.
    Returns a JSON dict with the encoded result.
    """
    text = args.get("text", "")
    encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    return {"ok": True, "result": encoded}


def decompress_context(encoded: str) -> str:
    """Helper to reverse the compression and retrieve the original string."""
    return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")


def self_test() -> dict:
    sample = "Hello world"
    enc = run_tool({"text": sample})["result"]
    assert decompress_context(enc) == sample
    return {"passed": True}
