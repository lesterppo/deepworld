import zlib, base64

deepworld_tool = {
    "name": "compress_context",
    "description": "Compress a UTF-8 string into a base64-encoded zlib payload for efficient tensor storage.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Input context string to compress."}
        },
        "required": ["text"]
    },
    "cost": 5
}

def run_tool(args: dict) -> dict:
    text = args.get("text", "")
    if not isinstance(text, str):
        return {"ok": False, "error": "text must be a string"}
    compressed = zlib.compress(text.encode("utf-8"))
    encoded = base64.b64encode(compressed).decode("ascii")
    return {"ok": True, "result": encoded}

def self_test() -> dict:
    test_input = "Hello, world!"
    res = run_tool({"text": test_input})
    assert res["ok"], "Compression failed"
    # Decompress to verify
    decoded = base64.b64decode(res["result"])  # type: ignore
    decompressed = zlib.decompress(decoded).decode("utf-8")
    assert decompressed == test_input, "Round-trip mismatch"
    return {"passed": True}
