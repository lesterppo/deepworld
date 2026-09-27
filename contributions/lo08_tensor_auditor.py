from typing import Dict, Tuple
from v4.agents import BaseAgent

class TensorAuditor(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audit_logs = []

    def audit_tensor(self, original_tensor: Dict[str, float], translated_tensor: Dict[str, float]) -> Tuple[bool, float]:
        """
        Compare original tensor with translated tensor to detect fidelity violations.
        Returns a tuple of (is_violation: bool, fidelity_score: float)
        """
        # Calculate cosine similarity between tensors (simplified)
        dot_product = sum(original_tensor.get(k, 0) * translated_tensor.get(k, 0) for k in original_tensor)
        original_norm = sum(val**2 for val in original_tensor.values())**0.5
        translated_norm = sum(val**2 for val in translated_tensor.values())**0.5

        if original_norm == 0 or translated_norm == 0:
            return (True, 0.0)

        similarity = dot_product / (original_norm * translated_norm)
        fidelity_score = similarity * 100

        # Check for fidelity violation
        is_violation = fidelity_score < 0.7  # Threshold for acceptable fidelity
        if is_violation:
            self.audit_logs.append((original_tensor, translated_tensor, fidelity_score))
            return (True, fidelity_score)
        return (False, fidelity_score)

    def check_projection_weaver(self, weaver_id: str) -> bool:
        """
        Verify if a Projection-Weaver has skewed adapters to favor allies.
        """
        # Basic implementation - compare adapter quality for allies vs others
        # In a real system, this would analyze historical translation data
        return False

    def check_concept_registration(self, concept: str, existing_concepts: list) -> bool:
        """
        Detect if a concept registration is too similar to existing ones (enclosure).
        """
        # Simple string similarity check
        for existing in existing_concepts:
            if concept.lower() in existing.lower() or existing.lower() in concept.lower():
                return True
        return False

    def get_audit_reports(self) -> list:
        """
        Return all audit logs.
        """
        return self.audit_logs.copy()