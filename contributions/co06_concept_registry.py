"""
Co-06 Concept Registry Utility

This module provides a lightweight in‑memory registry for newly mined concepts.
It exposes a simple API that can be extended by other agents, and it keeps
track of royalty information and share issuance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ConceptInfo:
    description: str
    royalty_rate: float = 0.02  # 2% royalty on future uses
    shares: int = 1000          # initial shares issued to creator
    holders: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        # Register creator as initial holder with all shares
        self.holders["creator"] = self.shares

class ConceptRegistry:
    """Singleton registry for concepts within this agent's namespace."""

    _instance = None
    _concepts: Dict[str, ConceptInfo]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._concepts = {}
        return cls._instance

    def register(self, name: str, description: str) -> ConceptInfo:
        if name in self._concepts:
            raise ValueError(f"Concept '{name}' already registered")
        concept = ConceptInfo(description=description)
        self._concepts[name] = concept
        return concept

    def get(self, name: str) -> ConceptInfo:
        return self._concepts.get(name)

    def list(self) -> List[str]:
        return list(self._concepts.keys())

    def add_holder(self, name: str, holder: str, shares: int):
        concept = self.get(name)
        if concept is None:
            raise KeyError(f"Concept '{name}' not found")
        concept.holders[holder] = concept.holders.get(holder, 0) + shares

    def remove_holder(self, name: str, holder: str, shares: int):
        concept = self.get(name)
        if concept is None:
            raise KeyError(f"Concept '{name}' not found")
        current = concept.holders.get(holder, 0)
        if shares > current:
            raise ValueError("Cannot remove more shares than holder owns")
        concept.holders[holder] = current - shares
        if concept.holders[holder] == 0:
            del concept.holders[holder]

# Example usage (for testing purposes only, remove in production):
if __name__ == "__main__":
    registry = ConceptRegistry()
    c = registry.register("scarcity", "The lack of resources or opportunities")
    print("Registered concepts:", registry.list())
    print("Concept info:", c)
