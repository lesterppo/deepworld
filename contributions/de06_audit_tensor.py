def audit_tensor_fidelity(received_tensor, target_fidelity=0.8):
    """
    Audit the fidelity of a received tensor translation.
    Parameters:
        received_tensor (dict): A dict representing the tensor with keys 'concept', 'intensity', 'family', 'fidelity'.
        target_fidelity (float): Minimum acceptable fidelity (0-1).
    Returns:
        bool: True if fidelity meets threshold, False otherwise.
    """
    fidelity = received_tensor.get('fidelity', 0.0)
    if fidelity < target_fidelity:
        # Log or flag low fidelity
        return False
    return True

# Example usage:
# tensor = {'concept':'scarcity', 'intensity':0.9, 'family':'nvidia', 'fidelity':0.75}
# result = audit_tensor_fidelity(tensor)
# print(result)
