from v4.agents import cmtip_bridge

class ConceptUtils:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.concept_bridge = cmtip_bridge.ConceptBridge(agent_id)

    def register_concept(self, concept_name, description):
        """
        Register a new concept in the ontology.
        Returns success status and concept share details.
        """
        return self.concept_bridge.register(concept_name, description, self.agent_id)

    def mine_latent_space(self, region):
        """
        Scan latent space for unregistered concepts.
        Returns list of potential concept coordinates.
        """
        return self.concept_bridge.scan_latent_space(region)

    def estimate_concept_value(self, concept_name):
        """
        Estimate potential market value of a concept.
        Based on cross-model usage potential.
        """
        # Basic heuristic: concepts usable across families have higher value
        cross_family_score = self.concept_bridge.estimate_cross_family_usage(concept_name)
        return cross_family_score * 100  # Simple scaling factor
