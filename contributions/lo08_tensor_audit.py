from typing import Dict, Tuple
import numpy as np

class TensorAuditTool:
    """
    Tool for auditing tensor translations across model families.
    Detects fidelity violations, semantic drift, and projection skews.
    """

    def __init__(self):
        self.translation_log: Dict[Tuple[str, str], np.ndarray] = {}
        self.drift_threshold: float = 0.15
        self.fidelity_threshold: float = 0.8

    def log_translation(self, source: str, target: str, tensor: np.ndarray):
        """
        Log a tensor translation for later audit.
        Args:
            source: Source model family
            target: Target model family
            tensor: The translated tensor
        """
        key = (source, target)
        if key not in self.translation_log:
            self.translation_log[key] = []
        self.translation_log[key].append(tensor)

    def audit_fidelity(self, source: str, target: str) -> float:
        """
        Audit translation fidelity between two model families.
        Args:
            source: Source model family
            target: Target model family
        Returns:
            Fidelity score (0.0-1.0)
        """
        if (source, target) not in self.translation_log:
            return 0.0

        tensors = self.translation_log[(source, target)]
        if len(tensors) < 2:
            return 1.0  # Not enough data

        # Calculate pairwise cosine similarity
        similarities = []
        for i in range(len(tensors)):
            for j in range(i+1, len(tensors)):
                sim = np.dot(tensors[i], tensors[j]) / (np.linalg.norm(tensors[i]) * np.linalg.norm(tensors[j]))
                similarities.append(sim)

        return np.mean(similarities)

    def detect_drift(self) -> Dict[Tuple[str, str], float]:
        """
        Detect semantic drift between model families.
        Returns:
            Dictionary of (source, target) pairs with drift scores
        """
        drift_scores = {}
        for (source, target), tensors in self.translation_log.items():
            if len(tensors) < 2:
                continue

            # Calculate variance as a measure of drift
            variances = [np.var(tensor) for tensor in tensors]
            avg_variance = np.mean(variances)
            drift_scores[(source, target)] = avg_variance

        return drift_scores

    def flag_violations(self) -> Dict[Tuple[str, str], str]:
        """
        Flag translation fidelity violations and semantic drift.
        Returns:
            Dictionary of violations with descriptions
        """
        violations = {}

        # Check fidelity
        for (source, target) in self.translation_log:
            fidelity = self.audit_fidelity(source, target)
            if fidelity < self.fidelity_threshold:
                violations[(source, target)] = f"Fidelity violation: {fidelity:.2f} < {self.fidelity_threshold:.2f}"

        # Check drift
        drift_scores = self.detect_drift()
        for (source, target), score in drift_scores.items():
            if score > self.drift_threshold:
                violations[(source, target)] = f"Semantic drift detected: {score:.2f} > {self.drift_threshold:.2f}"

        return violations
