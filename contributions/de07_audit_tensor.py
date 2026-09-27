"""Audit utilities for tensor consistency and fidelity checks.

This module provides a lightweight function to verify a received tensor
against a reference tensor for fidelity violations. It can be used by
Loss-Miner agents to flag cross‑family translations that deviate beyond
acceptable thresholds.

The function is intentionally simple so it can be imported by
existing agents without pulling in heavy dependencies.
"""

import numpy as np

def check_fidelity(received, reference, threshold=0.3):
    """Return True if the received tensor is within *threshold* of reference.

    Parameters
    ----------
    received : np.ndarray
        Tensor received by the agent (projected to its model family).
    reference : np.ndarray
        Ground‑truth tensor or a trusted reference.
    threshold : float
        Maximum allowed Euclidean distance relative to the norm of
        the reference tensor.

    Returns
    -------
    bool
        ``True`` if fidelity is acceptable, ``False`` otherwise.
    """
    if received.shape != reference.shape:
        return False
    diff = np.linalg.norm(received - reference)
    norm = np.linalg.norm(reference)
    return diff / norm <= threshold

# Example usage (for local testing only):
# if __name__ == "__main__":
#     ref = np.array([1, 2, 3])
#     rec = np.array([1.1, 1.9, 3.05])
#     print(check_fidelity(rec, ref))
