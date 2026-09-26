import numpy as np

def audit_tensor_translation(original, translated, threshold=0.7):
    """
    Audit tensor translation fidelity between two model families.
    Returns True if fidelity is above threshold, False otherwise.
    """
    # Calculate cosine similarity
    dot_product = np.dot(original, translated)
    norm_a = np.linalg.norm(original)
    norm_b = np.linalg.norm(translated)
    similarity = dot_product / (norm_a * norm_b)
    
    return similarity >= threshold

def detect_skewed_projection(adapter, reference, threshold=0.1):
    """
    Check if a projection adapter has been maliciously skewed.
    Returns True if deviation from reference is above threshold.
    """
    # Calculate mean squared error
    mse = np.mean((adapter - reference) ** 2)
    return mse > threshold