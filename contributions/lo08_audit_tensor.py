"""Audit module for tensor translation fidelity checks.

Provides functions to compute similarity between source and target tensors
and detect potential fidelity violations in cross‑family projections.
"""

from typing import List, Tuple
import numpy as np

# A simple cosine similarity helper

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Return cosine similarity between two vectors."""
    a_norm = a / np.linalg.norm(a)
    b_norm = b / np.linalg.norm(b)
    return float(np.dot(a_norm, b_norm))

# Main audit function

def audit_tensor_translation(source: np.ndarray, target: np.ndarray, threshold: float = 0.8) -> Tuple[bool, float]:
    """Audit a single tensor translation.

    Parameters
    ----------
    source: np.ndarray
        Original tensor embedding in source model family.
    target: np.ndarray
        Projected tensor embedding in target model family.
    threshold: float
        Minimum acceptable similarity. Below this indicates a fidelity violation.

    Returns
    -------
    Tuple[bool, float]
        (is_fidelity_ok, similarity_score)
    """
    similarity = cosine_similarity(source, target)
    is_ok = similarity >= threshold
    return is_ok, similarity

# Batch audit helper

def audit_batch(source_list: List[np.ndarray], target_list: List[np.ndarray], threshold: float = 0.8) -> List[Tuple[bool, float]]:
    """Audit a batch of tensor translations."""
    results = []
    for src, tgt in zip(source_list, target_list):
        results.append(audit_tensor_translation(src, tgt, threshold))
    return results

# Simple test harness
if __name__ == "__main__":
    # Create dummy tensors
    src = np.random.randn(128)
    tgt_good = src + np.random.randn(128) * 0.01  # small noise
    tgt_bad = np.random.randn(128)  # unrelated
    print("Good similarity:", audit_tensor_translation(src, tgt_good, 0.9))
    print("Bad similarity:", audit_tensor_translation(src, tgt_bad, 0.9))
