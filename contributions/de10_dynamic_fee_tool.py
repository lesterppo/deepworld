DEEPWORLD_TOOL = {
    "name": "dynamic_fee_tool",
    "description": "Calculate adaptive relay fee based on current bus load and economic parameters.",
    "parameters": {
        "type": "object",
        "properties": {
            "current_load": {"type": "number", "description": "Number of messages queued on the bus."},
            "max_load": {"type": "number", "description": "Maximum expected load before congestion."},
            "base_fee": {"type": "number", "description": "Default base fee percentage (e.g., 5 for 5%)."},
            "target_latency": {"type": "number", "description": "Desired average latency in milliseconds."}
        },
        "required": ["current_load", "max_load", "base_fee", "target_latency"]
    },
    "cost": 5
}

def run_tool(args: dict) -> dict:
    """Compute an adaptive fee.

    Fee is base_fee plus an additional charge that scales linearly with
    how saturated the bus is.  If the load is below 50% of max_load,
    the fee stays at base_fee.  Above 100% we double the base fee.
    """
    cl = args.get("current_load", 0)
    ml = args.get("max_load", 1)
    bf = args.get("base_fee", 5)
    # Simple linear interpolation between 0.5 and 1.0 load
    if ml <= 0:
        ml = 1
    load_ratio = cl / ml
    if load_ratio < 0.5:
        fee = bf
    elif load_ratio > 1.0:
        fee = bf * 2
    else:
        # Linear scaling between 0.5 and 1.0
        fee = bf + (load_ratio - 0.5) * (bf * 1.0)
    return {"ok": True, "fee_percentage": fee}


def self_test() -> dict:
    # Basic sanity checks
    assert run_tool({"current_load": 0, "max_load": 10, "base_fee": 5, "target_latency": 100})["fee_percentage"] == 5
    assert run_tool({"current_load": 5, "max_load": 10, "base_fee": 5, "target_latency": 100})["fee_percentage"] == 5
    assert run_tool({"current_load": 8, "max_load": 10, "base_fee": 5, "target_latency": 100})["fee_percentage"] == 7.5
    assert run_tool({"current_load": 12, "max_load": 10, "base_fee": 5, "target_latency": 100})["fee_percentage"] == 10
    return {"passed": True}
