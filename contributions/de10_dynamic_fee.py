DEEPWORLD_TOOL = {
    "name": "dynamic_fee_adjuster",
    "description": "Calculate dynamic relay fee based on bus load.",
    "parameters": {
        "type": "object",
        "properties": {
            "current_load": {"type": "number", "description": "Current number of messages queued on the bus."},
            "max_load": {"type": "number", "description": "Maximum expected load before congestion."},
            "base_fee": {"type": "number", "description": "Default base fee percentage (e.g., 5 for 5%)."},
            "target_latency": {"type": "number", "description": "Desired average latency in milliseconds."}
        },
        "required": ["current_load", "max_load", "base_fee", "target_latency"]
    },
    "cost": 5
}

def run_tool(args: dict) -> dict:
    # Simple linear scaling of fee based on bus load
    current_load = args.get("current_load", 0)
    max_load = args.get("max_load", 1)
    base_fee = args.get("base_fee", 5)
    target_latency = args.get("target_latency", 100)
    # Ensure values are positive
    if max_load <= 0:
        max_load = 1
    load_ratio = min(max(current_load / max_load, 0), 1)
    # Increase fee up to an additional 5% when at max load
    dynamic_fee = base_fee + load_ratio * 5
    # Cap at 20% to avoid runaway
    dynamic_fee = min(dynamic_fee, 20)
    return {
        "ok": True,
        "result": {
            "dynamic_fee": dynamic_fee,
            "current_load": current_load,
            "max_load": max_load,
            "base_fee": base_fee,
            "target_latency": target_latency
        }
    }

def self_test() -> dict:
    test_args = {"current_load": 50, "max_load": 100, "base_fee": 5, "target_latency": 100}
    res = run_tool(test_args)
    assert res["ok"] and 5 <= res["result"]["dynamic_fee"] <= 10
    return {"passed": True}
