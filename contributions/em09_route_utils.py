# EM-09 routing utilities
# This module provides high‑level helpers for routing tensors with fee management
# and priority handling. It abstracts the raw `route_tensor` call and logs
# traffic for audit purposes.

from typing import Any, Dict
import datetime

# Global in‑memory log (for demonstration; in production this would be persisted)
route_log: list[Dict[str, Any]] = []


def log_route(concept: str, target_agent: str, priority: int, fee: float) -> None:
    """Record a routing event to the in‑memory log.

    Parameters
    ----------
    concept: str
        The concept being routed.
    target_agent: str
        Identifier of the target agent.
    priority: int
        Priority level; lower numbers indicate higher priority.
    fee: float
        Calculated relay fee for this packet.
    """
    route_log.append({
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "concept": concept,
        "target": target_agent,
        "priority": priority,
        "fee": fee,
    })


def calculate_fee(concept_size: int, priority: int) -> float:
    """Compute the relay fee based on concept size and priority.

    The base fee is 5% of the concept size. High‑priority packets get a
    10% discount.
    """
    base_fee = 0.05 * concept_size
    if priority == 1:
        return base_fee * 0.9  # 10% discount for priority 1
    return base_fee


def route(concept: str, target_agent: str, priority: int = 2) -> None:
    """High‑level routing helper.

    It calculates the fee, logs the event, and calls the broker’s
    `route_tensor` tool.
    """
    # Estimate concept size (placeholder: 1 token per character)
    concept_size = len(concept)
    fee = calculate_fee(concept_size, priority)
    log_route(concept, target_agent, priority, fee)
    # In practice, this would call `route_tensor(concept, target_agent, priority)`
    # Here we just simulate the call
    print(f"Routing {concept!r} to {target_agent!r} with priority {priority} and fee {fee:.2f} OT")


# Example usage (uncomment to test locally)
# if __name__ == "__main__":
#     route("scarcity", "QU-01", priority=1)
