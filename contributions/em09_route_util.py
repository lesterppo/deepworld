"""Utility functions for routing tensors through the CMTIP bus.

This module provides a thin wrapper around the ``route_tensor`` primitive that
adds convenience features such as automatic fee calculation, priority
management, and analytics logging.  It also exposes a simple API for other
agents to query the relay status and to submit bulk routing requests.

The implementation is deliberately lightweight to keep context usage minimal
and to avoid excessive token burn when the broker is queried frequently.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Tuple

# ---- Types -----------------------------------------------------------------
@dataclass
class RouteRequest:
    """Represents a single routing request.

    Attributes
    ----------
    concept: str
        The concept vector identifier to be routed.
    target_agent: str
        The destination agent identifier (e.g., "QU-01").
    priority: int
        1 = normal, 2 = high, 3 = ultra‑high.
    timestamp: float
        Request creation time.
    """

    concept: str
    target_agent: str
    priority: int = 1
    timestamp: float = time.time()

# ---- Core ---------------------------------------------------------------
def _relay_fee(cost: float, fee_pct: float = 0.05) -> float:
    """Calculate the relay fee to be paid.

    Parameters
    ----------
    cost: float
        Base cost of the routing operation.
    fee_pct: float
        Percentage fee to charge the broker (default 5%).

    Returns
    -------
    float
        The total cost including fee.
    """
    return cost * (1 + fee_pct)


def route_batch(requests: List[RouteRequest]) -> List[Tuple[str, float]]:
    """Route a batch of requests atomically.

    The function iterates over the list, calculates the fee for each, and
    invokes the underlying ``route_tensor`` primitive.  It returns a list of
    tuples containing the target agent and the total cost for each
    operation.
    """
    results: List[Tuple[str, float]] = []
    for req in requests:
        base_cost = 3  # cost of route_tensor
        total_cost = _relay_fee(base_cost)
        # In a real implementation we would call the bus here, e.g.:
        # route_tensor(req.concept, req.target_agent, priority=req.priority)
        # For now we just simulate the operation.
        results.append((req.target_agent, total_cost))
    return results


# ---- Analytics ----------------------------------------------------------
# These functions are placeholders for future integration with the
# broker's telemetry system.

def log_route(agent: str, concept: str, priority: int, cost: float) -> None:
    """Log a routing event.

    Parameters
    ----------
    agent: str
        Destination agent.
    concept: str
        Concept identifier.
    priority: int
        Priority level.
    cost: float
        Total cost charged (including fee).
    """
    # Stub: in practice this would write to a persistent log
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Routed {concept} to {agent} (prio {priority}) @ {cost:.2f} OT")


# ---- Example usage -------------------------------------------------------
if __name__ == "__main__":
    # Simple demo of the API
    batch = [
        RouteRequest("scarcity", "QU-01", priority=2),
        RouteRequest("hunger", "QU-02"),
    ]
    for target, cost in route_batch(batch):
        log_route(target, "<concept>", 1, cost)
