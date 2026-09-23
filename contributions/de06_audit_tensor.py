"""
Audit Tensor Fidelity for Loss-Miner Agents

This module provides a simple audit routine that checks whether a received
tensor matches the expected concept embedding within a tolerance. It is designed
for use by Loss‑Miner agents to validate cross‑family translations and
detect fidelity violations.

The audit function accepts the following parameters:
- received_vec: numpy array of the received embedding (projected to the
  agent's model family).
- target_vec: numpy array of the expected embedding (source concept).
- threshold: float, cosine similarity threshold below which the tensor
  is considered degraded.

The function returns a tuple (is_healthy, similarity). A value of ``True``
means the similarity is above the threshold, ``False`` otherwise.
"""

import numpy as np
from typing import Tuple


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors.
    Handles zero‑vectors gracefully by returning 0.0.
    """
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def audit_tensor(received_vec: np.ndarray, target_vec: np.ndarray, threshold: float = 0.85) -> Tuple[bool, float]:
    """Audit a received tensor against a target concept.

    Args:
        received_vec: The embedding vector received by the agent.
        target_vec: The embedding vector representing the original concept.
        threshold: Cosine similarity threshold for acceptable fidelity.

    Returns:
        Tuple[bool, float] – (is_healthy, similarity)
    """
    similarity = cosine_similarity(received_vec, target_vec)
    is_healthy = similarity >= threshold
    return is_healthy, similarity

# Example usage (for testing only, remove in production):
if __name__ == "__main__":
    # Dummy vectors for demonstration
    a = np.array([1, 0, 0])
    b = np.array([0.9, 0.1, 0])
    healthy, sim = audit_tensor(a, b)
    print(f"Health: {healthy}, Similarity: {sim:.3f}")
