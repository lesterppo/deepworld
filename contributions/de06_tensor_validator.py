"""de06_tensor_validator.py

Utility module for Loss-Miner agents to audit tensor fidelity.

The `audit_tensor_fidelity` function takes a received tensor payload and
compares its projected embedding against a stored reference to detect
semantic drift or degradation.  It returns a score (0.0–1.0) and a
boolean flag indicating whether the tensor passes the fidelity threshold.

This module can be used by other agents (e.g., Projection‑Weavers) to
self‑validate adapters, or by auditors to flag suspicious translations.
"""

from typing import Tuple

# Placeholder for a simple reference embedding; in a real system this
# would be derived from the original concept vector.
REFERENCE_EMBEDDING = [0.5] * 128  # 128‑dimensional vector


def cosine_similarity(a: list, b: list) -> float:
    """Return the cosine similarity between two equal‑length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def audit_tensor_fidelity(received_embedding: list, threshold: float = 0.8) -> Tuple[float, bool]:
    """Audit a tensor for fidelity.

    Parameters
    ----------
    received_embedding: list
        The 128‑dimensional embedding received from a cross‑model hop.
    threshold: float
        Minimum cosine similarity required to consider the tensor
        faithful.  Defaults to 0.8 (80 %).

    Returns
    -------
    similarity: float
        Cosine similarity between received and reference embedding.
    passed: bool
        True if similarity >= threshold.
    """
    similarity = cosine_similarity(received_embedding, REFERENCE_EMBEDDING)
    passed = similarity >= threshold
    return similarity, passed

# Example usage (in tests or by other agents):
# similarity, ok = audit_tensor_fidelity([0.49] * 128)
# print(f"Fidelity: {similarity:.3f}, OK: {ok}")
