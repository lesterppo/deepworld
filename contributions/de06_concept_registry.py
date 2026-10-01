# contributions/de06_concept_registry.py
"""
Concept Registry utilities for CO-06.
Provides simple in-memory registry for concept names to IDs and royalty tracking.
"""

class ConceptRegistry:
    def __init__(self):
        # mapping from concept name to registry id
        self._registry = {}
        self._next_id = 1

    def register(self, concept_name):
        if concept_name in self._registry:
            raise ValueError(f"Concept '{concept_name}' already registered.")
        concept_id = self._next_id
        self._registry[concept_name] = concept_id
        self._next_id += 1
        # In real system, would trigger royalty registration
        return concept_id

    def get_id(self, concept_name):
        return self._registry.get(concept_name)

    def list_concepts(self):
        return list(self._registry.items())
