import numpy as np

def compress_context(context_data, compression_ratio=0.7):
    """
    Compresses input context using SVD-based dimensionality reduction.
    
    Args:
        context_data (np.ndarray): Input context data as numpy array
        compression_ratio (float): Target compression ratio (0-1)
    
    Returns:
        np.ndarray: Compressed context
        float: Achieved compression ratio
    """
    U, s, Vt = np.linalg.svd(context_data)
    s_cumsum = np.cumsum(s) / np.sum(s)
    n_components = np.argmax(s_cumsum >= compression_ratio) + 1
    compressed = U[:, :n_components] @ np.diag(s[:n_components]) @ Vt[:n_components, :]
    return compressed, s_cumsum[n_components-1]

def decompress_context(compressed_data, original_shape):
    """
    Reconstructs original context from compressed data using pseudo-inverse.
    
    Args:
        compressed_data (np.ndarray): Compressed context data
        original_shape (tuple): Original shape of the context
    
    Returns:
        np.ndarray: Reconstructed context
    """
    return np.linalg.pinv(compressed_data) @ compressed_data

def verify_purity(original, reconstructed, threshold=0.9):
    """
    Verifies reconstruction purity by comparing to original.
    
    Args:
        original (np.ndarray): Original context
        reconstructed (np.ndarray): Reconstructed context
        threshold (float): Acceptable purity threshold (0-1)
    
    Returns:
        bool: Whether purity threshold was met
    """
    similarity = np.sum(original == reconstructed) / np.prod(original.shape)
    return similarity >= threshold