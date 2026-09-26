# PR-03: Projection Utilities
# This module provides helper functions for training and managing cross‑model projection adapters.
# It is designed to be lightweight, testable, and easy to integrate into the CMTIP bridge.

from typing import Dict, Any
import numpy as np

# In‑memory registry for adapters. In a full implementation this would persist.
_ADAPTER_REGISTRY: Dict[str, Any] = {}


def adapter_key(source_family: str, target_family: str) -> str:
    """Return a deterministic key for an adapter based on source/target families."""
    return f"{source_family}->{target_family}"


def train_projection(source_family: str, target_family: str, investment: int = 15) -> None:
    """Simulate training of a cross‑model projection adapter.

    Parameters
    ----------
    source_family: str
        The family of the source model (e.g., "nvidia").
    target_family: str
        The family of the target model (e.g., "google").
    investment: int, default 15
        Amount of OT invested. Higher values increase fidelity.
    """
    key = adapter_key(source_family, target_family)
    # Simulate fidelity as a function of investment.
    fidelity = min(0.75, 0.25 + investment * 0.01)  # baseline 0.25 + 0.01 per OT
    # Store a simple representation of the adapter.
    _ADAPTER_REGISTRY[key] = {
        "source": source_family,
        "target": target_family,
        "fidelity": fidelity,
        "investment": investment,
    }
    print(f"[PR-03] Trained adapter {key} with fidelity {fidelity:.3f}")


def get_adapter(source_family: str, target_family: str) -> Dict[str, Any]:
    """Retrieve a trained adapter. Raises KeyError if not found."""
    key = adapter_key(source_family, target_family)
    return _ADAPTER_REGISTRY[key]


def list_adapters() -> Dict[str, Dict[str, Any]]:
    """Return all registered adapters."""
    return _ADAPTER_REGISTRY.copy()

# Example usage (for testing purposes only; remove in production).
if __name__ == "__main__":
    train_projection("nvidia", "google", 20)
    print(list_adapters())
