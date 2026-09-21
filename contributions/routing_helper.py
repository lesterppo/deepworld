"""Utility module for managing routing rules within the CMTIP bus relay.

This module provides helper functions to:
1. Register a new routing rule with priority.
2. Remove an existing rule.
3. Query the current routing table.

These helpers make it easier for other infrastructure components to programmatically
control the flow of tensors without directly manipulating the internal data
structures.
"""

from typing import Dict, Tuple, List

# In-memory routing table: target_agent -> (priority, handler)
_routing_table: Dict[str, Tuple[int, callable]] = {}


def register_route(target_agent: str, priority: int, handler: callable) -> None:
    """Register a routing rule.

    Parameters
    ----------
    target_agent : str
        Identifier of the target agent.
    priority : int
        Lower values mean higher priority.
    handler : callable
        Function to be called when a tensor destined for the target
        needs to be processed.
    """
    _routing_table[target_agent] = (priority, handler)


def remove_route(target_agent: str) -> None:
    """Remove a routing rule for the given target agent."""
    _routing_table.pop(target_agent, None)


def get_route(target_agent: str) -> Tuple[int, callable] | None:
    """Retrieve the routing rule for a target agent, if it exists."""
    return _routing_table.get(target_agent)


def list_routes() -> List[Tuple[str, int]]:
    """Return a list of all registered routes as (target_agent, priority)."""
    return [(agent, prio) for agent, (prio, _) in _routing_table.items()]

# Example usage:
# register_route("agent_X", 10, lambda tensor: print("Routing to X", tensor))

