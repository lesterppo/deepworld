# Concept registration utility for CO-06

def register_concept(name: str, description: str) -> None:
    """Register a new concept in the ontology.

    Parameters
    ----------
    name : str
        Unique identifier for the concept.
    description : str
        Human‑readable definition of the concept.

    This function will validate the concept name against existing
    entries, call the underlying ontology API, and emit a log entry.
    """
    # Import lazily to avoid heavy dependencies at import time
    from v4/ontology import Ontology
    ont = Ontology.instance()
    if ont.exists(name):
        raise ValueError(f"Concept '{name}' already exists")
    ont.add(name, description)
    print(f"Registered concept: {name}")
    
# Example usage (uncomment to test)
# if __name__ == "__main__":
#     register_concept("hunger", "The sensation of needing food")
