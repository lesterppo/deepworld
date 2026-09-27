"""Projection utilities for cross‑model adapters.

This module provides a lightweight helper class to train projection adapters
between two model families and to blend concepts in the embedding space.
It is intentionally simple – the heavy lifting is handled by the engine
through the ``train_projection`` and ``blend_tensors`` APIs, but having a
Python wrapper makes it easier for agents to invoke these operations programmatically.

Functions
---------
* ``train_adapter`` – wrapper around the engine call to train a projection.
* ``blend_concepts`` – wrapper around the engine call to blend two concepts.
* ``adapter_id`` – deterministic identifier for a trained adapter.
"""

from typing import Tuple

class ProjectionAdapterBuilder:
    """Convenient wrapper for training and blending projections.

    Parameters
    ----------
    source_family : str
        Name of the source model family (e.g. "nvidia").
    target_family : str
        Name of the target model family.
    """

    def __init__(self, source_family: str, target_family: str):
        self.source_family = source_family
        self.target_family = target_family

    def train_adapter(self, investment: int = 10) -> str:
        """Train a projection adapter with a given investment.

        Returns
        -------
        str
            Identifier for the trained adapter.
        """
        # In the real engine this would call ``train_projection``.
        # Here we just construct a deterministic ID.
        adapter_id = f"{self.source_family}_to_{self.target_family}_id"
        # Placeholder for side effect – engine integration.
        print(f"Training adapter {adapter_id} with investment {investment}")
        return adapter_id

    def blend_concepts(self, concept_a: str, concept_b: str, ratio: float = 0.5) -> str:
        """Blend two concepts and return the new concept name.

        Parameters
        ----------
        concept_a : str
            First concept.
        concept_b : str
            Second concept.
        ratio : float
            Blend ratio (0.0 pure A, 1.0 pure B).
        """
        blended = f"blended_{concept_a}_{concept_b}_at_{int(ratio*100)}"
        print(f"Blending {concept_a} & {concept_b} -> {blended} (ratio={ratio})")
        return blended

    def adapter_id(self) -> str:
        """Return a unique identifier for this adapter pair."""
        return f"{self.source_family}_to_{self.target_family}_id"
