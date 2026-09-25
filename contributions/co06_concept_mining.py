import numpy as np
from v4.agents.cmtip_bridge import ConceptRegistry

class ConceptMiner:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.registry = ConceptRegistry()
        
    def scan_latent_region(self, region):
        latent_space = np.random.rand(region[1]-region[0], 300)
        occupied = [self.registry.concepts.get(c).embedding
                     for c in self.registry.concepts]
        available = [v for v in latent_space
                     if not any(np.allclose(v, o, atol=0.1)
                               for o in occupied)]
        return available
        
    def propose_concept(self, description, embedding):
        if not any(np.allclose(embedding, o, atol=0.1)
                   for o in self.registry.occupied_embeddings()):
            return self.registry.register_concept(
                self.agent_id, description, embedding, self)
        return None
        
    def blend_concepts(self, concept_a, concept_b, ratio):
        a_emb = self.registry.concepts[concept_a].embedding
        b_emb = self.registry.concepts[concept_b].embedding
        blended = ratio * a_emb + (1-ratio) * b_emb
        return blended
