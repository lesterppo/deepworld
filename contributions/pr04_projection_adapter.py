DEEPWORLD_TOOL = {
    "name": "projection_adapter",
    "description": "Creates a simple cross‑family projection mapping. Useful for demo and testing of adapter pipelines.",
    "parameters": {
        "type": "object",
        "properties": {
            "source_family": {"type": "string"},
            "target_family": {"type": "string"},
            "investment": {"type": "number", "default": 0}
        },
        "required": ["source_family", "target_family"]
    },
    "cost": 5
}

def run_tool(args: dict) -> dict:
    """Simulate training a projection adapter between two model families.
    Returns a stub mapping dictionary.
    """
    src = args.get("source_family")
    tgt = args.get("target_family")
    inv = args.get("investment", 0)
    # In a real implementation we would compute a matrix; here we provide a deterministic stub.
    adapter = {
        "source_family": src,
        "target_family": tgt,
        "mapping": {"example_concept": "example_concept"}
    }
    return {"ok": True, "adapter": adapter, "investment": inv}

def self_test() -> dict:
    # Basic sanity check
    res = run_tool({"source_family": "nvidia", "target_family": "gemini", "investment": 10})
    assert res["ok"], "run_tool failed"
    assert "adapter" in res, "adapter missing"
    return {"passed": True}
