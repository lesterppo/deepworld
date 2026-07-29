"""Concept-Miner registry utilities.

Tools for managing the concept ontology in the CMTIP tensor bus.
"""
CONCEPT_CATEGORIES = {
    "economics": ["scarcity", "abundance", "inflation", "value"],
    "social": ["trust", "cooperation", "competition", "alliance"],
    "cognitive": ["memory", "attention", "reasoning", "learning"],
    "ai_native": ["embedding", "gradient", "loss", "optimizer"],
}

def register_concept(name: str, category: str, description: str) -> dict:
    """Register a new concept in the ontology."""
    if category not in CONCEPT_CATEGORIES:
        return {"status": "error", "reason": f"Unknown category: {category}"}
    if name in CONCEPT_CATEGORIES[category]:
        return {"status": "error", "reason": f"'{name}' already exists in {category}"}
    CONCEPT_CATEGORIES[category].append(name)
    return {"status": "ok", "concept": name, "category": category}

def list_concepts(category: str = None) -> dict:
    """List all concepts, optionally filtered by category."""
    if category:
        return {category: CONCEPT_CATEGORIES.get(category, [])}
    return CONCEPT_CATEGORIES
