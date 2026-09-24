from typing import Dict, List, Optional
import numpy as np

class ConceptRegistry:
    def __init__(self):
        self.registry: Dict[str, Dict] = {}
        self.shareholders: Dict[str, Dict[int, int]] = {}

    def register_concept(self, name: str, description: str, owner: str) -> bool:
        """
        Register a new concept in the latent space.
        """
        if name in self.registry:
            return False

        self.registry[name] = {
            'description': description,
            'owner': owner,
            'dividends': 0.0
        }
        self.shareholders[name] = {owner: 1000}
        return True

    def update_dividends(self, name: str, amount: float) -> None:
        """
        Update dividends for a concept.
        """
        if name in self.registry:
            self.registry[name]['dividends'] += amount

    def get_dividends(self, owner: str) -> float:
        """
        Get total dividends for an owner.
        """
        total = 0.0
        for concept in self.registry.values():
            if concept['owner'] == owner:
                total += concept['dividends']
        return total

    def transfer_shares(self, concept: str, from_owner: str, to_owner: str, shares: int) -> bool:
        """
        Transfer shares between owners.
        """
        if concept not in self.shareholders or from_owner not in self.shareholders[concept]:
            return False

        if self.shareholders[concept][from_owner] < shares:
            return False

        self.shareholders[concept][from_owner] -= shares
        if to_owner in self.shareholders[concept]:
            self.shareholders[concept][to_owner] += shares
        else:
            self.shareholders[concept][to_owner] = shares

        return True