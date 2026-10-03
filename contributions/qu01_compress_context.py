DEEPWORLD_TOOL = {
    "name": "qu01_compress_context",
    "description": "Compress a context string into a base64 zlib payload.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string"}
        },
        "required": ["text"]
    },
    "cost": 2
}

def run_tool(args: dict) -> dict:
    import zlib, base64
    try:
        payload = base64.b64encode(zlib.compress(args["text"].encode()))
        return {"ok": True, "result": payload.decode()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def self_test() -> dict:
    assert run_tool({"text": "test"})["ok"]
    return {"passed": True}
