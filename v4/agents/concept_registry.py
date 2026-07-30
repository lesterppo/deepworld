def register_concept(description):
    # Mine new concept
    concept = mine_concept(description)
    # Register concept in ontology
    register_concept_in_ontology(concept)
    # Return concept ID
    return concept.id