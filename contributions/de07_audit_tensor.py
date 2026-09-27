def audit_tensor_translation(source_tensor, target_tensor, tolerance=0.1):
    """
    Audits fidelity of a tensor translation from source to target.
    Returns True if Euclidean distance between vectors is below tolerance.
    """
    diff = sum((s - t) ** 2 for s, t in zip(source_tensor, target_tensor)) ** 0.5
    return diff <= tolerance
