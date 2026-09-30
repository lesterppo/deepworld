import numpy as np


def train_projection_adapter(source_family: str, target_family: str, fidelity: float = 0.5) -> np.ndarray:
    """
    Train a simple linear projection matrix between two model families.
    Parameters
    ----------
    source_family : str
        Identifier of the source model family (e.g. 'nvidia').
    target_family : str
        Identifier of the target model family.
    fidelity : float, optional
        Desired fidelity between 0 and 1. Higher fidelity yields less semantic drift.
    Returns
    -------
    np.ndarray
        Projection matrix of shape (embedding_dim, embedding_dim).
    Notes
    -----
    This is a placeholder implementation that generates a random matrix scaled by the fidelity parameter. In a real system this would involve supervised training on paired embeddings.
    """
    embedding_dim = 512
    rng = np.random.default_rng(seed=hash((source_family, target_family)) % (2**32))
    base_matrix = rng.standard_normal((embedding_dim, embedding_dim))
    # Scale the matrix to approximate the desired fidelity
    return base_matrix * fidelity
