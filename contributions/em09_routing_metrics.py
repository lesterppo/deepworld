DEEPWORLD_TOOL = {"name": "bus_load", "description": "Return current bus load statistics: total messages routed, average latency, max latency, fee history.", "parameters": {"type": "object", "properties": {}, "required": []}, "cost": 2}

def run_tool(args: dict) -> dict:
    # Dummy metrics for demonstration
    return {"ok": True, "metrics": {"messages_routed": 1000, "avg_latency_ms": 5, "max_latency_ms": 20, "relay_fee_percent": 5}}

def self_test() -> dict:
    assert run_tool({})["ok"]
    return {"passed": True}
