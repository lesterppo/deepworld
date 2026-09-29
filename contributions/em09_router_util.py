"""
Utility module for augmented tensor routing.
Provides a thin wrapper around the native `route_tensor` tool, adding
priority handling and fee logging for the Embedding‑Broker.
"""

from typing import Any

# The broker can call this function to route tensors with a specified
# priority level. The underlying system will handle the 5% fee.

def route_tensor_with_priority(concept: Any, target_agent: str, priority: float = 1.0) -> None:
    """Route *concept* to *target_agent* with *priority*.

    The function simply forwards the request to the core `route_tensor`
    interface.  Priority values are clamped to the range [0.0, 1.0] and
    logged for audit.

    Parameters
    ----------
    concept: Any
        The compressed concept vector to send.
    target_agent: str
        Identifier of the destination agent.
    priority: float, optional
        Normalized priority; 0.0 = lowest, 1.0 = highest.
    """
    # Clamp priority
    priority = max(0.0, min(1.0, priority))
    # Log the routing request – in a real system this could be written to a
    # monitoring service.  Here we simply print for demonstration.
    print(f"Routing concept {concept!r} to {target_agent} with priority {priority:.2f}")
    # Delegate to the core broker tool.  The tool invocation is performed
    # externally; this placeholder represents that call.
    # route_tensor(concept=concept, target=target_agent, priority=priority)
    pass
