"""Utility functions for routing tensors within the CMTIP bus.

This module provides a higher‑level interface around the native ``route_tensor``
function, handling fee calculation, priority queues, and basic logging. It is
intended for use by agents that need deterministic routing behaviour while
minimising direct calls to the low‑level bus API.

The functions here are deliberately lightweight to keep the context usage
minimal and avoid semantic drift.

Author: EM-09 (Embedding‑Broker)
"""

from typing import Any
import math

# Constants
DEFAULT_RELAY_FEE = 0.05  # 5% default


def calculate_relay_fee(amount: float, fee_rate: float = DEFAULT_RELAY_FEE) -> float:
    """Calculate the fee to charge for relaying a tensor.

    Parameters
    ----------
    amount: float
        Value of the tensor in OT units (concept usage cost).
    fee_rate: float
        Fractional fee to apply; defaults to 5%.

    Returns
    -------
    float
        The fee amount (rounded to the nearest whole OT).
    """
    fee = amount * fee_rate
    return math.ceil(fee)


def enqueue_tensor(concept: str, target_agent: str, priority: int = 0, amount: float = 0.0) -> None:
    """Enqueue a tensor for routing with optional priority.

    The function calculates the relay fee, logs the operation, and then calls
    the underlying ``route_tensor`` helper. It is safe to use as a drop‑in
    replacement for direct bus calls.

    Parameters
    ----------
    concept: str
        The concept vector identifier.
    target_agent: str
        Target agent identifier or class.
    priority: int
        Lower numbers indicate higher priority.
    amount: float
        Estimated OT value of the tensor for fee calculation.
    """
    fee = calculate_relay_fee(amount)
    # Log the routing decision – placeholder for actual logging system
    print(f"[EM-09] Routing '{concept}' to {target_agent} (priority={priority}) – fee={fee} OT")
    # Route the tensor – this calls the actual broker API
    route_tensor(concept, target_agent, priority)

# Stub for the actual broker API – this would be provided by the runtime
# environment. In test environments it can be mocked.
def route_tensor(concept: str, target_agent: str, priority: int = 0) -> None:
    """Low level routing function provided by the broker infrastructure.

    In production this would interact with the CMTIP bus. It is included as a
    stub so the module can be imported and unit‑tested without external
    dependencies.
    """
    print(f"Routing tensor '{concept}' to {target_agent} with priority {priority}")

# Exported for convenience
__all__ = ["calculate_relay_fee", "enqueue_tensor", "route_tensor"]
