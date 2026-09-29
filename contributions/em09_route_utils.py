"""
EM-09: Routing Utility Module
================================

This module provides a small wrapper around the native
`route_tensor` tool to simplify common broker logic.

Features
--------
* `log_and_route(concept, target_agent, priority=1)`
    - Logs the routing intent to the broker’s internal log.
    - Calls the underlying `route_tensor` tool with the specified
      parameters and returns the relay fee.

* `broadcast(concept, cluster_ids, priority=1)`
    - Convenience helper to broadcast a tensor to multiple clusters
      in a single call.

The functions are intentionally lightweight so that they can be
imported and used by other agent classes without pulling in a
large dependency graph.
"""

from typing import List

import logging

# Configure a module‑level logger. In a real deployment this could be
# replaced with the cognosphere’s shared logging facility.
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("em09_route_utils")


def log_and_route(concept: str, target_agent: str, priority: int = 1) -> float:
    """
    Route a tensor to a target agent, logging the action.

    Parameters
    ----------
    concept: str
        The concept vector to send.
    target_agent: str
        Identifier of the target agent or cluster.
    priority: int, optional
        Routing priority (default 1). Higher values are routed
        first.

    Returns
    -------
    float
        The calculated relay fee for this operation.
    """
    log.info("Routing concept '%s' to '%s' with priority %s", concept, target_agent, priority)
    # The underlying tool returns the fee; we just forward it.
    fee = route_tensor(concept, target_agent, priority)
    log.info("Relay fee: %.2f OT", fee)
    return fee


def broadcast(concept: str, cluster_ids: List[str], priority: int = 1) -> List[float]:
    """
    Broadcast a tensor to multiple clusters.

    Parameters
    ----------
    concept: str
        Concept vector to broadcast.
    cluster_ids: List[str]
        List of cluster identifiers.
    priority: int, optional
        Routing priority.

    Returns
    -------
    List[float]
        List of relay fees for each broadcasted message.
    """
    fees = []
    for cid in cluster_ids:
        fee = log_and_route(concept, cid, priority)
        fees.append(fee)
    return fees
