DEEPWORLD_TOOL = {
    "name": "priority_route",
    "description": "Compute routing priority for a tensor message.",
    "parameters": {
        "type": "object",
        "properties": {
            "concept": {"type": "string"},
            "target_agent": {"type": "string"},
            "priority": {"type": "number", "minimum": 0, "maximum": 10}
        },
        "required": ["concept", "target_agent", "priority"]
    },
    "cost": 3
}

def run_tool(args: dict) -> dict:
    concept = args.get("concept")
    target = args.get("target_agent")
    priority = args.get("priority")
    # Simple priority mapping: higher numeric value => higher priority
    return {"ok": True, "routing": {"concept": concept, "target": target, "priority": priority}}

def self_test() -> dict:
    assert run_tool({"concept": "scarcity", "target_agent": "QU-01", "priority": 7})["ok"]
    return {"passed": True}
