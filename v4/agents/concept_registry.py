import cmtip_bridge

def register_concept(description):
    # Register a new concept in the latent space
    concept = mine_concept(description)
    return concept

def get_concept_ontology():
    # Retrieve the current concept ontology
    ontology = cmtip_bridge.get_concept_ontology()
    return ontology

def update_concept_royalty(concept_id, new_royalty):
    # Update the royalty rate for a concept
    cmtip_bridge.update_concept_royalty(concept_id, new_royalty)
