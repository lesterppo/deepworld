import numpy as np

class ProjectionAdapter:
    """
    Simple projection adapter between two model families.
    Stores a weight matrix W that maps source embeddings to target space.
    """

    def __init__(self, source_family: str, target_family: str, dim: int = 512):
        self.source_family = source_family
        self.target_family = target_family
        self.dim = dim
        # Initialize with random orthogonal matrix for stability
        q, _ = np.linalg.qr(np.random.randn(dim, dim))
        self.W = q

    def transform(self, vector: np.ndarray) -> np.ndarray:
        """Apply projection to a source embedding.
        Args:
            vector: 1-D numpy array of shape (dim,)
        Returns:
            projected vector in target space.
        """
        if vector.shape[0] != self.dim:
            raise ValueError("Vector dimensionality does not match adapter dim")
        return self.W @ vector

    def learn(self, source_batch: np.ndarray, target_batch: np.ndarray, lr: float = 1e-3, epochs: int = 10):
        """Fine‑tune the projection matrix using gradient descent.
        Args:
            source_batch: (N, dim) array of source embeddings.
            target_batch: (N, dim) array of target embeddings.
            lr: learning rate.
            epochs: number of training epochs.
        """
        for _ in range(epochs):
            preds = source_batch @ self.W.T
            loss = np.mean((preds - target_batch) ** 2)
            grad = 2 * (source_batch.T @ (preds - target_batch)) / source_batch.shape[0]
            self.W -= lr * grad

    def __repr__(self):
        return f"ProjectionAdapter({self.source_family}->{self.target_family}, dim={self.dim})"
