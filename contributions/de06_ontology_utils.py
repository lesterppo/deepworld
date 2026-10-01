# de06_ontology_utils.py
"""
Utility module for managing concept registry and ontology utilities.
This module provides a lightweight in-memory registry that can be
extended to interface with persistent storage or external services.
"""

from __future__ import annotations
from typing import Dict, List, Tuple

class OntologyRegistry:
    """Simple in-memory ontology registry.

    The registry stores concept names mapped to their descriptions.
    It provides basic CRUD operations that can be extended to support
    persistence, duplicate checking, and royalty tracking.
    """

    def __init__(self) -> None:
        self._concepts: Dict[str, str] = {}

    def register(self, name: str, description: str) -> bool:
        """Register a new concept.

        Args:
            name: The unique concept name.
            description: A concise definition.

        Returns:
            True if registration succeeded.

        Raises:
            ValueError: If the concept name already exists.
        """
        if name in self._concepts:
            raise ValueError(f"Concept '{name}' is already registered.")
        self._concepts[name] = description
        return True

    def get(self, name: str) -> str | None:
        """Retrieve the description for a registered concept."""
        return self._concepts.get(name)

    def exists(self, name: str) -> bool:
        """Check whether a concept name is registered."""
        return name in self._concepts

    def list(self) -> List[Tuple[str, str]]:
        """Return a list of (name, description) tuples for all concepts."""
        return list(self._concepts.items())

    def unregister(self, name: str) -> bool:
        """Remove a concept from the registry.

        Returns True if the concept was removed, False if it did not exist.
        """
        return self._concepts.pop(name, None) is not None

# ---------------------------------------------------------------------
# Example usage (for testing only, not executed in production)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    reg = OntologyRegistry()
    reg.register("scarcity", "A state of limited availability.")
    print(reg.get("scarcity"))
    print(reg.list())
