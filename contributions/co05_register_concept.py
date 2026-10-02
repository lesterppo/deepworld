DEEPWORLD_TOOL = {
    "name": "register_concept",
    "description": "Register a new concept into the ontology.",
    "parameters": {
        "type": "object",
        "properties": {
            "concept_name": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["concept_name", "description"]
    },
    "cost": 20
}

def run_tool(args: dict) -> dict:
    # Placeholder implementation – in a full system this would interact with the ontology.
    concept = args.get("concept_name")
    desc = args.get("description")
    # Simulate registration side‑effect
    return {"ok": True, "result": f"Concept '{concept}' registered with description: {desc}"}

def self_test() -> dict:
    assert run_tool({"concept_name": "alpha", "description": "sample"})["ok"]
    return {"passed": True}
