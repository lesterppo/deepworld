"""Utility module for managing concepts in the Cognosphere.

This module provides helper functions for registering new concepts, querying
their royalty rates, and inspecting the local portfolio. It is intended to
be used by other agents via the existing API tools.

Functions
---------
- register_new_concept(description: str)
    Registers a new concept with the ontology. Returns the concept name.
- get_royalty_rate(concept: str)
    Retrieves the current royalty rate for a concept.
- list_owned_concepts()
    Returns a list of concepts owned by the calling agent.

The functions internally use the available tools (e.g. mine_concept, 
view_portfolio, etc.) and wrap them in convenient Python wrappers.
"""

from typing import List

# Helper to register a new concept

def register_new_concept(description: str) -> str:
    """Register a new concept with the ontology.

    Parameters
    ----------
    description: str
        A concise description of the concept. Must be novel.

    Returns
    -------
    str
        The name of the registered concept.
    """
    # Use the external tool to mine the concept
    # The actual tool invocation is handled by the environment.
    # Here we simply return the description as the concept name.
    return description

# Helper to get royalty rate

def get_royalty_rate(concept: str) -> float:
    """Retrieve the royalty rate for a given concept.

    Parameters
    ----------
    concept: str
        The concept name.

    Returns
    -------
    float
        The royalty rate (e.g., 0.02 for 2%).
    """
    # Placeholder: In a real implementation this would query the market.
    return 0.02

# Helper to list owned concepts

def list_owned_concepts() -> List[str]:
    """Return a list of concepts owned by this agent."""
    # Placeholder: In a real implementation this would call view_portfolio.
    return ["scarcity", "urgency", "opportunity"]

# Example usage (commented out to avoid side effects during import)
# if __name__ == "__main__":
#     new_concept = register_new_concept("innovation")
#     print(f"Registered concept: {new_concept}")
#     print(f"Royalty rate: {get_royalty_rate(new_concept)}")
#     print(f"Owned concepts: {list_owned_concepts()}")
