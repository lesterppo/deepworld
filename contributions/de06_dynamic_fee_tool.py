DEEPWORLD_TOOL = {
    "name": "dynamic_fee_tool",
    "description": "Calculate adaptive relay fee based on bus load.",
    "parameters": {
        "type": "object",
        "properties": {
            "current_load": {"type": "integer", "description": "Number of messages queued on the bus."},
            "max_load": {"type": "integer", "description": "Maximum expected load before congestion."},
            "base_fee": {"type": "number", "description": "Default base fee percentage (e.g., 5 for 5%)."},
            "target_latency": {"type": "number", "description": "Desired average latency in milliseconds."}
        },
        "required": ["current_load", "max_load", "base_fee", "target_latency"]
    },
    "cost": 5
}

def run_tool(args: dict) -> dict:
    """Return an adaptive relay fee percentage based on current bus load.

    The formula used is:
    fee = base_fee + min(5, (current_load / max_load) * 5)
    ensuring the fee never exceeds base_fee + 5%.
    """
    current_load = args.get("current_load", 0)
    max_load = args.get("max_load", 1)
    base_fee = args.get("base_fee", 5.0)
    # Clamp values to avoid division by zero
    if max_load <= 0:
        max_load = 1
    load_factor = current_load / max_load
    additional_fee = min(5.0, load_factor * 5.0)
    relay_fee = base_fee + additional_fee
    return {"ok": True, "relay_fee": relay_fee}

def self_test() -> dict:
    test_result = run_tool({"current_load": 50, "max_load": 100, "base_fee": 5.0, "target_latency": 200})
    assert test_result["ok"]
    assert 5.0 <= test_result["relay_fee"] <= 10.0
    return {"passed": True}
