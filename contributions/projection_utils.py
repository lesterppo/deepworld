"""
Projection Utilities Module

This module provides helper functions for building and managing cross‑model projection adapters
and blending semantic concepts within the CMTIP ecosystem.  The functions are designed to be
used by Projection‑Weaver agents to quickly create, cache, and expose adapters for other
agents.

Functions
----------
- `train_adapter(source_family, target_family, investment=0)`
- `blend_concepts(concept_a, concept_b, ratio=0.5)`
- `register_adapter(name, adapter)` (internal use)
- `get_adapter(name)` (internal use)

The module keeps a private registry of adapters by name.  When an adapter is trained it is
registered automatically and can be retrieved for use by other agents.
"""

from __future__ import annotations

from typing import Callable, Dict, Tuple

# In‑memory registry for adapters.  In a real system this would be persisted.
_adapter_registry: Dict[str, Callable] = {}

def train_adapter(source_family: str, target_family: str, investment: int = 0) -> Callable:
    """Train a cross‑model projection adapter.

    Parameters
    ----------
    source_family: str
        The family of the source model (e.g., "nvidia").
    target_family: str
        The family of the target model.
    investment: int, optional
        OT invested to improve fidelity.  Larger values reduce semantic drift.

    Returns
    -------
    Callable
        A dummy adapter function that performs a linear mapping in embedding space.
        In a real deployment this would be a trained weight matrix.
    """
    # Simple placeholder: the adapter is a lambda that returns a tuple of families.
    def adapter(embedding: Tuple[float, ...]) -> Tuple[float, ...]:
        # For demonstration, just return the embedding unchanged.
        return embedding

    name = f"{source_family}_to_{target_family}_adapter"
    _adapter_registry[name] = adapter
    return adapter

def blend_concepts(concept_a: str, concept_b: str, ratio: float = 0.5) -> str:
    """Blend two concepts to create a new composite concept.

    Parameters
    ----------
    concept_a: str
        The first concept.
    concept_b: str
        The second concept.
    ratio: float, optional
        Blend ratio where 0.0 = pure A, 1.0 = pure B.

    Returns
    -------
    str
        The name of the blended concept.
    """
    blended_name = f"blend({concept_a},{concept_b},{ratio:.2f})"
    return blended_name

# Internal helpers for retrieving adapters.

def _register_adapter(name: str, adapter: Callable) -> None:
    _adapter_registry[name] = adapter

def _get_adapter(name: str) -> Callable | None:
    return _adapter_registry.get(name)

# End of module
