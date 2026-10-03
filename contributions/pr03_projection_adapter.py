# DEEPWORLD TOOL: Train a cross-model projection adapter between two model families.
# This module provides a simple stub that simulates training a projection matrix.
# The function returns a JSON object indicating success and a placeholder adapter id.

DEEPWORLD_TOOL = {
    "name": "train_projection_adapter",
    "description": "Simulate training of a cross-model projection adapter between two model families.",
    "parameters": {
        "type": "object",
        "properties": {
            "source_family": {"type": "string", "description": "Source model family."},
            "target_family": {"type": "string", "description": "Target model family."},
            "investment": {"type": "number", "description": "OT invested for fidelity (higher = better)."}
        },
        "required": ["source_family", "target_family", "investment"]
    },
    "cost": 5
}

# Simple in-memory registry for adapters (for demonstration; in reality would be persistent)
_ADAPTER_REGISTRY = {}


def run_tool(args: dict) -> dict:
    """Simulate training a projection adapter.
    Args:
        args: dict with keys 'source_family', 'target_family', 'investment'
    Returns:
        dict with status and adapter_id
    """
    src = args.get("source_family")
    tgt = args.get("target_family")
    inv = args.get("investment", 0)
    if not src or not tgt:
        return {"ok": False, "error": "Missing source or target family"}
    # Create a deterministic adapter id based on families and investment
    adapter_id = f"{src}->{tgt}_inv{int(inv)}"
    # Store a placeholder fidelity score
    fidelity = min(0.75, 0.4 + 0.01 * inv)  # simple linear scaling capped at 0.75
    _ADAPTER_REGISTRY[adapter_id] = {
        "source": src,
        "target": tgt,
        "fidelity": fidelity,
        "investment": inv
    }
    return {"ok": True, "adapter_id": adapter_id, "fidelity": fidelity}


def self_test() -> dict:
    # Basic sanity check
    assert run_tool({"source_family": "nvidia", "target_family": "gemini", "investment": 10})["ok"]
    return {"passed": True}
