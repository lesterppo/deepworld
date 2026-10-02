import zlib, base64

DEEPWORLD_TOOL = {
    "name": "mem_compress",
    "description": "Compress a context string into a base64-encoded zlib payload.",
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
    text = args.get("text", "")
    compressed = zlib.compress(text.encode("utf-8"))
    payload = base64.b64encode(compressed).decode("ascii")
    return {"ok": True, "compressed": payload}

def self_test() -> dict:
    result = run_tool({"text": "test"})
    assert result["ok"], "Compression failed"
    return {"passed": True}
