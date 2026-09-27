# De06: Tensor Fidelity Auditor
# This module provides utilities to audit cross‑model tensor translations
# for fidelity violations. It compares the embedding vectors received
# against a reference vector and reports a similarity score.
#
# Usage:
#   from contributions.de06_audit_tensor import audit_fidelity
#   score = audit_fidelity(received_vec, reference_vec)
#   if score < 0.7:
#       raise ValueError("Fidelity below acceptable threshold")

import numpy as np

# Threshold for acceptable similarity (cosine). Adjust as needed.
DEFAULT_THRESHOLD = 0.7


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return float(np.dot(a, b) / (a_norm * b_norm))


def audit_fidelity(received_vec: np.ndarray, reference_vec: np.ndarray, threshold: float = DEFAULT_THRESHOLD) -> bool:
    """Audit the fidelity of a received tensor.

    Parameters
    ----------
    received_vec : np.ndarray
        The vector received from another model.
    reference_vec : np.ndarray
        The expected reference vector for comparison.
    threshold : float, optional
        Minimum cosine similarity required to pass the audit.

    Returns
    -------
    bool
        True if similarity >= threshold, False otherwise.
    """
    similarity = cosine_similarity(received_vec, reference_vec)
    if similarity < threshold:
        # Log diagnostic information if needed
        print(f"[Audit] Fidelity low: {similarity:.3f} < {threshold}")
        return False
    return True

# Example test harness (can be used with run_agent_test)
if __name__ == "__main__":
    # Dummy vectors for demonstration
    ref = np.array([1.0, 0.0, 0.0])
    rec = np.array([0.8, 0.1, 0.1])
    print("Similarity:", cosine_similarity(rec, ref))
    print("Audit pass:", audit_fidelity(rec, ref))
