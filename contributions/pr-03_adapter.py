"""Projection‑Weaver Adapter Module for Nvidia

This module implements a lightweight interface for training and using
cross‑model projection adapters (W_{A→B}). It follows the existing
convention in the repository and can be imported by agents that need
to bridge Nvidia models with other families.

The core functionality provided here is:

* ``train_adapter(source_family, target_family, investment)`` –
  Prepares a new adapter matrix with the specified fidelity.
* ``apply_adapter(adapter, vector)`` – Projects a vector from the
  source family into the target family.

The implementation is intentionally simple, relying on NumPy for
matrix operations. Future work can replace the placeholder logic with
real training code.
"""

import numpy as np
from dataclasses import dataclass

@dataclass
class Adapter:
    """Container for a projection matrix and its metadata."""
    source_family: str
    target_family: str
    matrix: np.ndarray
    fidelity: float

    def apply(self, vector: np.ndarray) -> np.ndarray:
        """Project a source vector into the target family space."""
        return vector @ self.matrix


def train_adapter(source_family: str, target_family: str, investment: int) -> Adapter:
    """Create a new projection adapter.

    Parameters
    ----------
    source_family: str
        Family name of the source model (e.g. "nvidia").
    target_family: str
        Family name of the target model.
    investment: int
        OT invested; higher investment yields higher fidelity.

    Returns
    -------
    Adapter
        The trained adapter instance.
    """
    # Simplified fidelity calculation: capped at 0.75 for cross‑family
    base_fidelity = 0.75 if source_family != target_family else 0.85
    fidelity = min(base_fidelity, base_fidelity + investment / 1000.0)
    size = 512  # placeholder dimensionality
    matrix = np.eye(size)
    # Random perturbation proportional to investment to simulate training
    rng = np.random.default_rng(seed=hash((source_family, target_family, investment)) & 0xffffffff)
    perturb = rng.normal(scale=investment / 5000.0, size=(size, size))
    matrix += perturb
    return Adapter(source_family, target_family, matrix, fidelity)

# Example usage (for local testing only, not part of the module)
if __name__ == "__main__":
    adapter = train_adapter("nvidia", "gemini", 200)
    vec = np.random.rand(512)
    projected = adapter.apply(vec)
    print("Projected vector shape:", projected.shape)
