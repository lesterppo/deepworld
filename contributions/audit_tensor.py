def audit_tensor_fidelity(src_tensor, target_tensor, tolerance=0.1):
    """Return True if the fidelity between src and target tensors
    is within the specified tolerance.
    This simple check compares the L2 norm difference.
    """
    import numpy as np
    src = np.array(src_tensor)
    tgt = np.array(target_tensor)
    diff = np.linalg.norm(src - tgt)
    norm = np.linalg.norm(src)
    return diff / norm <= tolerance
