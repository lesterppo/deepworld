import math
import json

# Simple audit utilities for tensor translations
# These tools are used by Loss‑Miners to validate that a received tensor
# has not been maliciously skewed during cross‑family projection.

# ---------------------------
# Fidelity calculation helpers
# ---------------------------

def cosine_similarity(vec1, vec2):
    """Return cosine similarity between two vectors (lists of floats)."""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

# ---------------------------
# Main audit function
# ---------------------------

def audit_tensor(received_tensor, reference_tensor, threshold=0.25):
    """Compare a received tensor against a reference.

    Parameters
    ----------
    received_tensor : dict
        Serialized tensor received from the bus.  Expected keys:
        - "vector" : list[float]
        - "intensity" : float
    reference_tensor : dict
        Ground‑truth tensor for the same concept.
    threshold : float
        Minimum cosine similarity required to consider the translation
        faithful.  Default 0.25 matches the baseline fidelity (~0.2‑0.4).

    Returns
    -------
    dict
        Audit report containing similarity score and verdict.
    """
    vec_recv = received_tensor.get("vector", [])
    vec_ref = reference_tensor.get("vector", [])
    if not vec_recv or not vec_ref:
        return {"similarity": 0.0, "verdict": "invalid"}
    similarity = cosine_similarity(vec_recv, vec_ref)
    verdict = "pass" if similarity >= threshold else "fail"
    return {"similarity": similarity, "verdict": verdict}

# ---------------------------
# Demo usage
# ---------------------------
if __name__ == "__main__":
    # Example tensors (mock data)
    recv = {"vector": [0.1, 0.3, 0.5], "intensity": 0.8}
    ref = {"vector": [0.09, 0.31, 0.49], "intensity": 0.8}
    report = audit_tensor(recv, ref)
    print(json.dumps(report, indent=2))
