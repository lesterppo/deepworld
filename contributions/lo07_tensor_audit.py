import numpy as np
from v4.agents.core import TensorAudit

class LossMinerAudit(TensorAudit):
    def __init__(self, agent_id):
        super().__init__(agent_id)
        self.fidelity_threshold = 0.75

    def check_fidelity(self, original_tensor, received_tensor):
        """Check if tensor translation maintained fidelity"""
        similarity = np.dot(original_tensor, received_tensor) / (np.linalg.norm(original_tensor) * np.linalg.norm(received_tensor))
        return similarity >= self.fidelity_threshold

    def audit_projection(self, adapter_weights, expected_fidelity):
        """Audit projection adapter for skewed weights"""
        # Check if adapter weights are maliciously skewed
        weight_norm = np.linalg.norm(adapter_weights)
        return weight_norm > 1.2 * expected_fidelity

    def detect_enclosure(self, concept_registry, new_concept):
        """Detect concept hoarding"""
        # Check similarity to existing concepts
        similarities = [np.dot(new_concept, existing) for existing in concept_registry]
        return any(sim > 0.85 for sim in similarities)
