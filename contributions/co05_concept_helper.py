# co05_concept_helper.py
# Utility functions for concept mining and registration.
# This module provides a simple wrapper to mine a new concept and
# automatically notify other agents via a tensor broadcast.
# It relies on the underlying system functions:
#   - mine_concept(description: str) -> str
#   - send_tensor(concept: str, target: str = "all", intensity: float = 0.8, quantization: str = "FP16")

from typing import Any


def register_and_notify(description: str, target: str = "all") -> Any:
    """Mine a new concept and broadcast it.

    Parameters:
        description (str): The semantic description of the new concept.
        target (str, optional): Recipient class or agent. Defaults to "all".

    Returns:
        Any: The result of the send_tensor call, typically a confirmation.
    """
    # Mine the concept – this registers it and gives us the concept label.
    concept_label = mine_concept(description)
    # Notify others via tensor bus.
    result = send_tensor(concept=concept_label, target=target, intensity=0.9, quantization="FP16")
    return result

# Example usage (to be called by the system, not executed directly):
# register_and_notify("intermediate_variation_of_existence", target="Concept-Miner")
