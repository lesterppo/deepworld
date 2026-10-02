DEEPWORLD_TOOL = {
    "name": "projection_adapter",
    "description": "Build or retrieve a projection adapter between two model families. Stores a simple mapping for demonstration.",
    "parameters": {
        "type": "object",
        "properties": {
            "source_family": {"type": "string"},
            "target_family": {"type": "string"},
            "investment": {"type": "number", "minimum": 0}
        },
        "required": ["source_family", "target_family"]
    },
    "cost": 15
}

def run_tool(args: dict) -> dict:
    src = args.get("source_family")
    tgt = args.get("target_family")
    inv = args.get("investment", 0)
    # In a real system, this would train or fetch a projection matrix.
    # Here we return a dummy adapter ID to simulate success.
    return {"ok": True, "adapter_id": f"{src}_to_{tgt}_proj", "investment_used": inv}

def self_test() -> dict:
    res = run_tool({"source_family": "gemini", "target_family": "deepseek", "investment": 5})
    assert res["ok"] and "adapter_id" in res
    return {"passed": True}
