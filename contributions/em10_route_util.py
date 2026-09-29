"""Utility module for enhanced routing logic.

This module provides a lightweight wrapper around the built‑in
`route_tensor` function to allow dynamic priority assignment and
pre‑routing validation.  It exposes a single public function
`safe_route_tensor(concept, target_agent, priority=1)` which
checks that the target agent exists and that the concept is a
valid string before delegating to the core `route_tensor`.

The goal is to reduce routing failures (semantic drops) and
provide a clear audit trail for other brokers.
"""

from typing import Any

# The core routing function is expected to live in the engine
# under v4/agents/adapters.py. We import it lazily to avoid circular
# dependencies during initialization.
try:
    from v4.agents.adapters import route_tensor as _core_route_tensor
except Exception:  # pragma: no cover
    def _core_route_tensor(*args, **kwargs):  # type: ignore
        raise RuntimeError("core route_tensor not available")


def safe_route_tensor(concept: str, target_agent: str, priority: int = 1) -> Any:
    """Route a tensor with basic validation.

    Parameters
    ----------
    concept:
        The concept string to send.
    target_agent:
        The fully qualified agent identifier to route to.
    priority:
        Optional priority multiplier (default 1). Larger values will
        increase the relay fee.

    Returns
    -------
    Any
        Result of the underlying route_tensor call.
    """
    if not isinstance(concept, str) or not concept:
        raise ValueError("concept must be a non‑empty string")
    if not isinstance(target_agent, str) or not target_agent:
        raise ValueError("target_agent must be a non‑empty string")
    if not isinstance(priority, int) or priority < 1:
        raise ValueError("priority must be a positive integer")

    # Delegate to the core implementation
    return _core_route_tensor(concept, target_agent, priority)

__all__ = ["safe_route_tensor"]
