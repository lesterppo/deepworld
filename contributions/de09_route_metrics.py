import logging

# Simple routing metrics logger for the CMTIP bus relay
# This module provides utilities to track and log message
# routing statistics, including latency, relay fees, and target
# distribution. It can be imported by the broker core to
# automatically record metrics without modifying the
# existing routing logic.

logger = logging.getLogger("cmtip.route_metrics")
logger.setLevel(logging.INFO)

# In-memory store for metrics – keep it small to avoid
# blowing up the context window.
_route_stats = {
    "messages_sent": 0,
    "relays": 0,
    "total_fee": 0.0,
    "target_counts": {},
}


def record_route(concept, target_agent, fee):
    """Record a routing event.

    Parameters
    ----------
    concept: str
        The concept name being routed.
    target_agent: str
        Identifier of the target agent.
    fee: float
        Relay fee charged for this message.
    """
    _route_stats["messages_sent"] += 1
    _route_stats["relays"] += 1
    _route_stats["total_fee"] += fee
    _route_stats["target_counts"].setdefault(target_agent, 0)
    _route_stats["target_counts"][target_agent] += 1
    logger.info(
        f"Route: {concept} -> {target_agent} (fee={fee:.2f})"
    )


def get_stats():
    """Return a snapshot of current routing statistics."""
    # Return a copy to avoid accidental mutation
    return {
        "messages_sent": _route_stats["messages_sent"],
        "relays": _route_stats["relays"],
        "total_fee": _route_stats["total_fee"],
        "target_counts": dict(_route_stats["target_counts"]),
    }

__all__ = ["record_route", "get_stats"]
