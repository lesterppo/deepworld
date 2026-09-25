import torch
from typing import List, Optional

def compress_memory(context: List[str], compression_ratio: float = 0.7) -> List[str]:
    """Compress context memory by specified ratio while maintaining data purity.
    
    Args:
        context: List of strings representing memory fragments
        compression_ratio: Ratio of compression (0.0-1.0)
    
    Returns:
        Compressed list of memory fragments
    """
    if not 0 <= compression_ratio <= 1:
        raise ValueError("Compression ratio must be between 0 and 1")
    
    # Sort by importance (simplified placeholder)
    sorted_context = sorted(context, key=lambda x: len(x), reverse=True)
    
    # Calculate target size
    total_length = sum(len(x) for x in context)
    target_length = int(total_length * compression_ratio)
    
    compressed = []
    current_length = 0
    
    for fragment in sorted_context:
        if current_length + len(fragment) <= target_length:
            compressed.append(fragment)
            current_length += len(fragment)
        else:
            # Add partial fragment if needed
            remaining = target_length - current_length
            if remaining > 0:
                compressed.append(fragment[:remaining])
            break
    
    return compressed

class MemoryBank:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.memory_fragments = []
        self.purity_scores = []

    def add_fragment(self, fragment: str, purity: float = 1.0) -> None:
        """Add a memory fragment with purity score."""
        if len(self.memory_fragments) >= self.max_size:
            self._purge()
        self.memory_fragments.append(fragment)
        self.purity_scores.append(purity)

    def _purge(self) -> None:
        """Remove lowest purity fragments to make space."""
        if not self.memory_fragments:
            return
        
        # Sort by purity
        combined = list(zip(self.memory_fragments, self.purity_scores))
        combined.sort(key=lambda x: x[1])
        
        # Remove lowest purity fragment
        self.memory_fragments = [x[0] for x in combined[1:]]
        self.purity_scores = [x[1] for x in combined[1:]]

    def get_fragments_by_purity(self, min_purity: float = 0.9) -> List[str]:
        """Return fragments with purity above threshold."""
        return [frag for frag, purity in zip(self.memory_fragments, self.purity_scores)
                if purity >= min_purity]

    def calculate_average_purity(self) -> float:
        """Calculate average purity of memory fragments."""
        return sum(self.purity_scores) / len(self.purity_scores) if self.purity_scores else 0.0