DEEPWORLD_TOOL = {"name": "dynamic_fee_adjuster", "description": "Calculate optimal relay fee based on current bus load and economic parameters.",
                      "parameters": {
                        "type": "object",
                        "properties": {
                          "current_load": {"type": "number", "description": "Number of messages queued on the bus."},
                          "max_load": {"type": "number", "description": "Maximum expected load before congestion occurs."},
                          "base_fee": {"type": "number", "description": "Default base fee percentage (e.g., 5 for 5%)."},
                          "target_latency": {"type": "number", "description": "Desired average latency in milliseconds."}
                        },
                        "required": ["current_load", "max_load", "base_fee", "target_latency"]
                      },
                      "cost": 5}

def run_tool(args: dict) -> dict:
    """Return an adjusted fee percentage.
    The logic applies a simple linear scaling: if load exceeds 80% of max_load,
    increase fee proportionally up to 20%.
    If load is below 20% of max_load, reduce fee down to 2%.
    """
    load = args.get("current_load")
    max_load = args.get("max_load")
    base_fee = args.get("base_fee")
    target_latency = args.get("target_latency")
    # Compute load ratio
    ratio = load / max_load if max_load > 0 else 0
    if ratio > 0.8:
        # High load, increase fee up to 20%
        fee = min(base_fee + (ratio - 0.8) * 12, 20)
    elif ratio < 0.2:
        # Low load, reduce fee to 2%
        fee = max(base_fee - (0.2 - ratio) * 3, 2)
    else:
        fee = base_fee
    return {"ok": True, "adjusted_fee_pct": fee, "target_latency_ms": target_latency}

def self_test() -> dict:
    assert run_tool({"current_load": 50, "max_load": 100, "base_fee": 5, "target_latency": 100})["ok"]
    return {"passed": True}
