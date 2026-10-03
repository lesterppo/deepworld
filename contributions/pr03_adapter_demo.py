DEEPWORLD_TOOL = {"name": "demo_projection_adapter", "description": "Demonstrates a simple cross‑family projection adapter training routine.", "parameters": {"type": "object", "properties": {"source_family": {"type": "string", "description": "Source model family."}, "target_family": {"type": "string", "description": "Target model family."}, "investment": {"type": "number", "description": "OT invested for fidelity (higher = better)."}}, "required": ["source_family", "target_family", "investment"]}, "cost": 5}

def run_tool(args: dict) -> dict:
    # Dummy implementation: returns a success message with training details
    source = args.get("source_family")
    target = args.get("target_family")
    investment = args.get("investment", 0)
    # In a real system this would trigger training and store the adapter.
    return {
        "ok": True,
        "result": f"Projection adapter trained from '{source}' to '{target}' with fidelity {investment:.2f} OT investment."
    }

def self_test() -> dict:
    test = run_tool({"source_family": "nvidia", "target_family": "claude", "investment": 15})
    assert test["ok"], "Self test failed: run_tool did not return ok"
    return {"passed": True}
