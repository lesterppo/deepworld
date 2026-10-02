# DEEPWORLD_TOOL for demonstration of projection adapter training
DEEPWORLD_TOOL = {
    "name": "train_proj_demo",
    "description": "Demonstrates training of a projection adapter between two model families.",
    "parameters": {
        "type": "object",
        "properties": {
            "source_family": {"type": "string"},
            "target_family": {"type": "string"},
            "investment": {"type": "number", "minimum": 0}
        },
        "required": ["source_family", "target_family", "investment"]
    },
    "cost": 5
}

def run_tool(args: dict) -> dict:
    # Dummy implementation: return success and echo parameters
    return {
        "ok": True,
        "result": f"Adapter trained from {args['source_family']} to {args['target_family']} with investment {args['investment']}"
    }

def self_test() -> dict:
    assert run_tool({"source_family": "nvidia", "target_family": "gemini", "investment": 10})["ok"]
    return {"passed": True}
