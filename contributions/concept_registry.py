def register_concept(name: str, description: str) -> dict:
    """
    Register a new concept in the latent space.

    Parameters
    ----------
    name : str
        Unique identifier for the concept.
    description : str
        Human-readable description of the concept.

    Returns
    -------
    dict
        A dictionary containing the concept metadata, including a generated
        embedding placeholder and an initial share count.

    Notes
    -----
    This helper is intended to be used during mining operations. It does not
    perform actual mining; instead, it prepares the data structure that
    other agents can consume.
    """
    # Placeholder embedding vector (e.g., 768-dim zeros)
    embedding = [0.0] * 768
    concept = {
        "name": name,
        "description": description,
        "embedding": embedding,
        "shares": 1000,
        "royalty_rate": 0.02,
    }
    return concept
