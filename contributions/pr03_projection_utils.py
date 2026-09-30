"""
Projection utilities for cross-model adapters.

This module provides helper functions to construct and register
cross‑family projection adapters.  The implementation is a lightweight
stub suitable for simulation and testing; real adapters would
interact with the engine’s projection kernel.
"""

class ProjectionAdapter:
    """Simple representation of a projection matrix.

    In a full implementation this would wrap a learned weight matrix
    and expose forward / inverse transforms.  For now it records
    source/target families and a fidelity score.
    """
    def __init__(self, source_family: str, target_family: str, fidelity: float = 0.5):
        self.source_family = source_family
        self.target_family = target_family
        self.fidelity = fidelity

    def __repr__(self):
        return f"<ProjectionAdapter {self.source_family}->{self.target_family} fidelity={self.fidelity:.2f}>"


def create_projection_adapter(source_family: str, target_family: str, investment: float) -> ProjectionAdapter:
    """Create a new projection adapter.

    Parameters
    ----------
    source_family: str
        The originating model family.
    target_family: str
        The destination model family.
    investment: float
        Amount of OT invested; higher values produce higher fidelity.

    Returns
    -------
    ProjectionAdapter
        A new adapter instance.
    """
    # Fidelity is a simple linear function of investment for this stub.
    fidelity = min(1.0, 0.2 + 0.05 * investment)
    return ProjectionAdapter(source_family, target_family, fidelity)

# Example usage (for testing only):
# adapter = create_projection_adapter("nvidia", "gpt4o", 10)
# print(adapter)
