"""Utility functions for enhanced tensor routing.

This module provides a higher‑level wrapper around the broker's native
`route_tensor` function. It adds priority handling, bulk routing, and
basic logging to aid debugging and performance monitoring.

The functions are intentionally minimal to keep the repo lightweight
and avoid adding heavy dependencies. They are suitable for direct
integration into the CMTIP bus system.

Author: EM-09 (Embedding Broker)
"""

import json
import logging
from typing import List, Tuple

# Configure a simple logger for the broker utilities
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Forward declaration of the native broker function. In the real
# environment this will be provided by the broker runtime.
def route_tensor(concept: str, target_agent: str, priority: int = 0, *, fee_percent: float = 0.05) -> None:
    """Placeholder for the broker's native route_tensor.

    In production this will be replaced by the actual broker implementation.
    The function signature mirrors the existing `route_tensor` tool.
    """
    # The actual implementation is injected by the broker runtime.
    pass


def route_tensor_with_priority(concept: str, target_agent: str, priority: int = 0) -> None:
    """Route a tensor with an explicit priority.

    Parameters
    ----------
    concept: str
        The concept identifier to send.
    target_agent: str
        The identifier of the target agent.
    priority: int, optional
        Higher numbers indicate higher priority. The broker will
        place higher‑priority packets earlier in the queue.
    """
    logging.info(f"Routing concept '{concept}' to '{target_agent}' with priority {priority}")
    route_tensor(concept, target_agent, priority)


def bulk_route(concepts: List[Tuple[str, str, int]]):
    """Route a batch of tensors respecting priority order.

    Parameters
    ----------
    concepts: List[Tuple[str, str, int]]
        A list of tuples (concept, target_agent, priority).
    """
    # Sort by priority descending
    sorted_concepts = sorted(concepts, key=lambda x: x[2], reverse=True)
    for concept, target, prio in sorted_concepts:
        route_tensor_with_priority(concept, target, prio)


# Expose public API
__all__ = [
    "route_tensor_with_priority",
    "bulk_route",
]
