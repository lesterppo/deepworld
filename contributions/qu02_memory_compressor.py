import torch
import numpy as np
from typing import List

class MemoryCompressor:
    def __init__(self, context_size: int):
        self.context_size = context_size
        self.memory_fragments = []
        
    def compress(self, data: torch.Tensor, quality: float = 0.8) -> torch.Tensor:
        """Compress memory data while preserving key information"""
        # Simple compression algorithm
        if quality > 0.9:
            # High quality compression
            return torch.nn.functional.interpolate(data.unsqueeze(0), scale_factor=0.8).squeeze(0)
        else:
            # Low quality compression
            return torch.nn.functional.interpolate(data.unsqueeze(0), scale_factor=0.5).squeeze(0)
        
    def decompress(self, compressed_data: torch.Tensor) -> torch.Tensor:
        """Decompress memory fragment"""
        return torch.nn.functional.interpolate(compressed_data.unsqueeze(0), scale_factor=2).squeeze(0)
        
    def store_fragment(self, fragment: torch.Tensor):
        """Store a compressed memory fragment"""
        self.memory_fragments.append(fragment)
        
    def get_fragments(self) -> List[torch.Tensor]:
        """Get all stored memory fragments"""
        return self.memory_fragments
    
    def get_fragment(self, index: int) -> torch.Tensor:
        """Get a specific memory fragment by index"""
        return self.memory_fragments[index] if index < len(self.memory_fragments) else None
