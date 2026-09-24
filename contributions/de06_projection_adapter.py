class ProjectionAdapter:
    """
    ProjectionAdapter handles cross-model projection between source and target families.
    It stores a weight matrix W_{A->B} and provides methods to train, apply, and blend tensors.
    """

    def __init__(self, source_family: str, target_family: str):
        self.source_family = source_family
        self.target_family = target_family
        self.matrix = None  # placeholder for projection matrix

    def train(self, data: list, investment: int = 15):
        """
        Train the projection matrix using provided data samples.
        :param data: List of (source_vector, target_vector) tuples.
        :param investment: OT invested; higher yields better fidelity.
        """
        # Simple linear regression placeholder
        import numpy as np
        src = np.array([d[0] for d in data])
        tgt = np.array([d[1] for d in data])
        # Solve for W: tgt = src @ W
        W, *_ = np.linalg.lstsq(src, tgt, rcond=None)
        self.matrix = W
        return self.matrix

    def apply(self, vector):
        """
        Apply the trained projection to a source vector.
        """
        if self.matrix is None:
            raise RuntimeError("Projection matrix not trained.")
        return vector @ self.matrix

    def blend(self, vector_a, vector_b, ratio: float):
        """
        Blend two projected vectors.
        """
        return (1 - ratio) * vector_a + ratio * vector_b