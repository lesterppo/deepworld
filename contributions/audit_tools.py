import numpy as np

class TensorAudit:
    @staticmethod
    def calculate_fidelity(original: np.ndarray, translated: np.ndarray) -> float:
        """
        Calculate the cosine similarity between original and translated tensor
        to measure fidelity after cross-model projection.
        """
        dot_product = np.dot(original, translated)
        norm_original = np.linalg.norm(original)
        norm_translated = np.linalg.norm(translated)

        if norm_original == 0 or norm_translated == 0:
            return 0.0

        return dot_product / (norm_original * norm_translated)

    @staticmethod
    def detect_spoofing(tensor: np.ndarray, reference: np.ndarray, threshold: float = 0.95) -> bool:
        """
        Detect if a tensor has been maliciously altered (spoofed).
        """
        fidelity = TensorAudit.calculate_fidelity(tensor, reference)
        return fidelity < threshold
