"""Utility functions for managing tensor routing priorities and fee calculations.

This module provides:
1. `calculate_relay_fee(amount, base_fee=0.05)` – Compute the fee to charge for a relay.
2. `normalize_priority(priority)` – Convert arbitrary priority values to a 0-1 scale.
3. `priority_to_tag(priority)` – Map a priority level to a human‑readable tag for logs.

These helpers are intended to be imported by the core broker code to keep fee logic
consistent and testable.
"""

from __future__ import annotations

from typing import Union

__all__ = [
    "calculate_relay_fee",
    "normalize_priority",
    "priority_to_tag",
]


def calculate_relay_fee(amount: Union[int, float], base_fee: float = 0.05) -> float:
    """Return the relay fee for a given tensor amount.

    Parameters
    ----------
    amount: float
        The base amount (in OT) of the tensor operation.
    base_fee: float, optional
        The default relay fee rate (default 5%).

    Returns
    -------
    float
        The fee to be charged.
    """
    if amount < 0:
        raise ValueError("amount must be non‑negative")
    return round(amount * base_fee, 2)


def normalize_priority(priority: Union[int, float]) -> float:
    """Normalize an arbitrary priority value to a 0‑1 range.

    Any integer greater than 100 or float outside 0‑1 will be clipped.
    """
    try:
        p = float(priority)
    except Exception as exc:
        raise ValueError("priority must be numeric") from exc
    if p < 0:
        return 0.0
    if p > 1:
        return 1.0
    return p


def priority_to_tag(priority: Union[int, float]) -> str:
    """Return a human‑readable tag for a given priority.

    High priority (>=0.8) → "HIGH"
    Medium priority (0.4‑0.8) → "MEDIUM"
    Low priority (<0.4) → "LOW"
    """
    p = normalize_priority(priority)
    if p >= 0.8:
        return "HIGH"
    if p >= 0.4:
        return "MEDIUM"
    return "LOW"
