import numpy as np


def audit_cross_model_translation(source_vector, target_vector, tolerance=0.05):
    """Audit fidelity of a cross-model tensor translation.

    Parameters
    ----------
    source_vector : np.ndarray
        Original embedding in source model family.
    target_vector : np.ndarray
        Projected embedding received in target model family.
    tolerance : float, optional
        Acceptable relative difference between source and target norms.

    Returns
    -------
    bool
        ``True`` if fidelity is within tolerance, otherwise ``False``.
    float
        Relative norm difference.
    """
    if source_vector.ndim != 1 or target_vector.ndim != 1:
        raise ValueError("Vectors must be 1-D arrays")
    src_norm = np.linalg.norm(source_vector)
    tgt_norm = np.linalg.norm(target_vector)
    if src_norm == 0:
        return False, 0.0
    rel_diff = abs(src_norm - tgt_norm) / src_norm
    return rel_diff <= tolerance, rel_diff


def audit_tensor_pool(pool, target_family, tolerance=0.05):
    """Audit a collection of tensors from a source family to a target family.

    Parameters
    ----------
    pool : list[tuple[str, np.ndarray]]
        List of (concept, vector) tuples received from source family.
    target_family : str
        Name of target model family for which vectors were projected.
    tolerance : float, optional
        Acceptable relative difference.

    Returns
    -------
    dict
        Mapping of concept to a tuple (is_fidelity_ok, rel_diff).
    """
    results = {}
    for concept, vec in pool:
        # Assume we have a reference vector for this concept in source
        # family. In real code, fetch from a trusted repository.
        try:
            ref_vec = get_reference_vector(concept)
        except KeyError:
            # No reference available; skip
            continue
        ok, diff = audit_cross_model_translation(ref_vec, vec, tolerance)
        results[concept] = (ok, diff)
    return results


def get_reference_vector(concept):
    """Placeholder: In production, this would query a secure registry."""
    raise KeyError(f"Reference vector for {concept} not found")
