"""Routing utilities for the CMTIP bus relay.

This module provides helper functions used by the
Embedding‑Broker to route tensors efficiently.  The
functions are intentionally simple so they can be
imported by other brokers or by future adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

# A simple representation of a tensor message.
@dataclass
class TensorMessage:
    concept: str
    target_agent: str
    priority: int  # Lower value = higher priority
    intensity: float = 0.8  # Default intensity

# Global relay fee rate (5% default).  Brokers can override.
RELAY_FEE_RATE: float = 0.05


def calculate_relay_fee(amount: float, fee_rate: float = RELAY_FEE_RATE) -> float:
    """Return the fee to charge for a given amount.

    Parameters
    ----------
    amount: float
        The base cost of sending the tensor.
    fee_rate: float, optional
        The broker's % fee.  Defaults to 5%.
    """
    return amount * fee_rate


def enqueue_message(queue: Iterable[TensorMessage], msg: TensorMessage) -> list[TensorMessage]:
    """Insert *msg* into *queue* respecting priority.

    The queue is a list sorted by priority.  After insertion
    the list is re‑sorted.  This function returns the new
    queue.
    """
    new_queue = list(queue) + [msg]
    new_queue.sort(key=lambda m: m.priority)
    return new_queue


def route_batch(messages: Iterable[TensorMessage], fee_rate: float = RELAY_FEE_RATE) -> Tuple[list[TensorMessage], float]:
    """Process a batch of messages.

    Returns a tuple of (delivered_messages, total_fee).
    """
    delivered = []
    total_fee = 0.0
    for msg in messages:
        # Simulate delivery cost: 2 OT per tensor + fee
        base_cost = 2.0
        fee = calculate_relay_fee(base_cost, fee_rate)
        total_fee += fee
        delivered.append(msg)
    return delivered, total_fee

# Example usage for a broker:
#   queue = enqueue_message(queue, TensorMessage('scarcity', 'QU-01', 1))
#   delivered, fee = route_batch(queue)

"""End of routing utils."""
