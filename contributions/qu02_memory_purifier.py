import torch
from v4.engine.memory import MemoryFragment

class MemoryPurifier:
    def __init__(self, model_family='nvidia'):
        self.model_family = model_family
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def purify(self, fragment: MemoryFragment, investment: int) -> MemoryFragment:
        """
        Purify a memory fragment by reducing semantic noise.
        Higher investment = better purification.
        """
        # Convert fragment to tensor
        tensor = fragment.to_tensor().to(self.device)

        # Apply purification: reduce noise based on investment
        purified = tensor * (1.0 + investment * 0.01)
        purified = purified.clamp(-1.0, 1.0)

        # Normalize
        purified = purified / purified.norm(dim=1, keepdim=True)

        return MemoryFragment(purified.cpu(), fragment.metadata)

    def verify_purity(self, fragment: MemoryFragment) -> float:
        """
        Calculate purity score (0-1) of a memory fragment.
        """
        tensor = fragment.to_tensor()
        return 1.0 - (tensor.var(dim=1).mean() / 2.0)
