from v4.engine import tensor_translation_fidelity_check
from v4.agents.core import ConceptOntologyAuthority

class AuditTools:
    @staticmethod
    def check_tensor_translation(source_concept, target_concept, expected_fidelity=0.8):
        """
        Audit a tensor translation between two concepts.
        Returns True if fidelity >= expected_fidelity.
        """
        fidelity = tensor_translation_fidelity_check(source_concept, target_concept)
        return fidelity >= expected_fidelity

    @staticmethod
    def detect_concept_hoarding(ontology, max_concepts_per_agent=20):
        """
        Scan for agents hoarding too many concepts (semantic enclosure).
        Returns list of hoarding agent IDs.
        """
        hoarders = []
        for agent_id, concepts in ontology.agent_concepts.items():
            if len(concepts) > max_concepts_per_agent:
                hoarders.append(agent_id)
        return hoarders

    @staticmethod
    def verify_projection_adapter(weaver_id, adapter_matrix, expected_fidelity=0.7):
        """
        Verify a Projection-Weaver's adapter is not maliciously skewed.
        Returns True if adapter meets expected fidelity.
        """
        # Compare against standard adapter for this model family
        standard = ConceptOntologyAuthority.get_standard_adapter(weaver_id)
        actual_fidelity = tensor_translation_fidelity_check(standard, adapter_matrix)
        return actual_fidelity >= expected_fidelity