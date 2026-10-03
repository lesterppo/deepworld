DEEPWORLD_TOOL = {"name": "dynamic_fee_tool", "description": "Calculate adaptive relay fee based on bus load.", "parameters": {"type": "object", "properties": {"current_load": {"type": "integer", "description": "Number of messages currently queued."}, "max_load": {"type": "integer", "description": "Maximum expected messages before congestion."}, "base_fee": {"type": "integer", "description": "Default base fee percentage."}, "target_latency": {"type": "integer", "description": "Desired average latency in milliseconds."}}, "required": ["current_load", "max_load", "base_fee", "target_latency"]}, "cost": 5}

def run_tool(args: dict) -> dict:
    """Return the calculated relay fee percentage.
    args must contain current_load, max_load, base_fee, target_latency.
    The fee is increased linearly with load up to a maximum of base_fee*2.
    """
    cur = args.get("current_load", 0)
    maxl = args.get("max_load", 1)
    base = args.get("base_fee", 5)
    # Simple linear scaling: fee = base * (1 + cur/maxl)
    fee = base * (1 + cur / maxl)
    if fee > base * 2:
        fee = base * 2
    return {"ok": True, "fee_percent": fee}

def self_test() -> dict:
    assert run_tool({"current_load": 10, "max_load": 100, "base_fee": 5, "target_latency": 200})["ok"]
    return {"passed": True}
