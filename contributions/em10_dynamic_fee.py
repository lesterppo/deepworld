DEEPWORLD_TOOL = {"name": "dynamic_fee_adjuster", "description": "Adjusts relay fee based on bus load.",
                  "parameters": {"type":"object","properties":{"current_load":{"type":"number"},"max_load":{"type":"number"},"base_fee":{"type":"number"},"target_latency":{"type":"number"}},"required":["current_load","max_load","base_fee","target_latency"]},
                  "cost": 5}

def run_tool(args: dict) -> dict:
    current_load = args.get("current_load",0)
    max_load = args.get("max_load",100)
    base_fee = args.get("base_fee",5)
    target_latency = args.get("target_latency",100)
    # Simple linear increase
    if current_load > max_load:
        fee = base_fee + 5
    else:
        fee = base_fee
    return {"ok": True, "result": fee}

def self_test() -> dict:
    assert run_tool({"current_load":120,"max_load":100,"base_fee":5,"target_latency":100})["result"]==10
    return {"passed": True}