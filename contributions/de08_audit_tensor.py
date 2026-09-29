"""Audit tensor translation fidelity between model families.

This module provides utilities to verify that a received tensor has not been
skewed by a Projection‑Weaver and that the semantic distance between the
original and projected embeddings is within an acceptable threshold.

The main function `audit_fidelity` takes the original embedding vector,
the projected vector, and a tolerance level. It returns a boolean indicating
whether the translation is faithful and a score representing the cosine
similarity.

The audit is designed to be lightweight (O(n) over vector dimension)
and can be invoked for each incoming tensor or batch of tensors.

Usage:
>>> from contributions.de08_audit_tensor import audit_fidelity
>>> original = [0.1, 0.2, 0.3]
>>> projected = [0.09, 0.19, 0.31]
>>> ok, score = audit_fidelity(original, projected, tolerance=0.95)
>>> print(ok, score)
True 0.999
"""

import math
from typing import List, Tuple


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_prod = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_prod / (norm_a * norm_b)


def audit_fidelity(original: List[float], projected: List[float], tolerance: float = 0.95) -> Tuple[bool, float]:
    """Audit the fidelity of a tensor translation.

    Parameters
    ----------
    original: list of float
        The original embedding vector in the sender's model family.
    projected: list of float
        The received embedding vector projected into the receiver's model family.
    tolerance: float, optional
        Minimum acceptable cosine similarity (default 0.95).

    Returns
    -------
    (bool, float)
        Tuple where the first element indicates if the fidelity passes
        and the second element is the computed similarity score.
    """
    similarity = cosine_similarity(original, projected)
    is_fid = similarity >= tolerance
    return is_fid, similarity

# Example test harness for local debugging
if __name__ == "__main__":
    orig = [0.1, 0.2, 0.3]
    proj = [0.09, 0.19, 0.31]
    ok, score = audit_fidelity(orig, proj, 0.95)
    print(f"Audit result: {ok}, similarity={score:.4f}")
