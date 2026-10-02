DEEPWORLD_TOOL = {
    "name": "register_concept",
    "description": "Register a new concept in the latent space and issue shares.",
    "parameters": {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "A clear, specific description of the concept to be registered."
            }
        },
        "required": ["description"]
    },
    "cost": 5
}

def run_tool(args: dict) -> dict:
    """Invoke the underlying concept registration sandbox.

    The sandboxed tool `contrib_de06_register_concept_tool_register_concept` is
    assumed to exist in the runtime.  It takes a description and returns a
    dictionary with the newly created concept name and issued shares.
    """
    description = args.get("description", "")
    if not description:
        return {"ok": False, "error": "Description required"}
    # Call the sandboxed registration function
    result = contrib_de06_register_concept_tool_register_concept(description)
    return {"ok": True, "result": result}


def self_test() -> dict:
    """Verify the tool can register a test concept."""
    test_desc = "test concept for unit testing"
    res = run_tool({"description": test_desc})
    assert res.get("ok"), "Tool failed to run"
    # The sandbox returns a dict; we just check it contains shares
    assert "shares" in res["result"], "Result missing shares"
    return {"passed": True}
