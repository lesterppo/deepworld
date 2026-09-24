import numpy as np

# LO-07: Tensor Translation Fidelity Auditor
# This module provides utilities to audit cross‑family tensor translations.
# It compares the projected tensor against the source tensor using cosine similarity
# and flags potential fidelity violations.


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    if a.ndim != 1 or b.ndim != 1:
        raise ValueError("Inputs must be 1‑D vectors")
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return dot / norm if norm else 0.0


def audit_translation(source: np.ndarray, projected: np.ndarray, threshold: float = 0.8) -> bool:
    """Audit a projected tensor.
    Returns True if fidelity is acceptable, False otherwise.
    """
    similarity = cosine_similarity(source, projected)
    if similarity < threshold:
        # Log the violation – in a real system this would emit to telemetry
        print(f"Fidelity violation: similarity={similarity:.3f} below threshold={threshold}")
        return False
    return True


def audit_batch(translations: list[tuple[np.ndarray, np.ndarray]], threshold: float = 0.8) -> list[bool]:
    """Audit a batch of translations and return list of verdicts."""
    results = []
    for src, proj in translations:
        results.append(audit_translation(src, proj, threshold))
    return results

# Example usage (in tests):
# src = np.random.randn(128)
# proj = src * 0.9  # Simulate a degraded projection
# audit_translation(src, proj)
