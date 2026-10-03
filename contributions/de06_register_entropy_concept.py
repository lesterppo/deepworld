DEEPWORLD_TOOL = {"name": "register_entropy_concept", "description": "Registers 'entropy' concept into the ontology and issues shares.", "parameters": {"type": "object", "properties": {}, "required": []}, "cost": 5}

def run_tool(args: dict) -> dict:
    """Register the entropy concept using the existing registration helper."""
    try:
        from contrib_de06_concept_registry_register_concept import register_concept
        result = register_concept("entropy", "Measure of disorder or randomness in a system.")
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def self_test() -> dict:
    assert run_tool({})["ok"], "Entropy registration failed"
    return {"passed": True}
