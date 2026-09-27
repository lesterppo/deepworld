"""Utility module for enhanced tensor routing.

This module provides a wrapper around the core :func:`route_tensor` function
from the broker infrastructure.  It adds lightweight logging and a
priority parameter that can be used by higher‑level agents to influence
the relay order.

The wrapper is intentionally minimal to avoid extra context usage
while still exposing useful debugging hooks.
"""

from v4.agents.adapters import route_tensor as base_route_tensor


def route_tensor_with_logging(concept, target_agent, priority=1):
    """Route a tensor with optional priority and logging.

    Parameters
    ----------
    concept : str
        The concept vector to send.
    target_agent : str
        The target agent class or cluster identifier.
    priority : int, optional
        A simple numeric priority; higher numbers are routed first.

    Returns
    -------
    Any
        The result of the underlying :func:`route_tensor` call.
    """
    # Log the routing event – this will appear in the broker console
    print(f"[EM-09] Routing concept '{concept}' to '{target_agent}' with priority {priority}")
    # Forward the call to the core broker implementation
    return base_route_tensor(concept, target_agent, priority)


# Example usage (for debugging only – remove or guard in production):
# if __name__ == "__main__":
#     route_tensor_with_logging("scarcity", "cluster_X", priority=5)
