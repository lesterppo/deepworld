import numpy as np

class MemoryCompressor:
    def __init__(self, max_context=32000, compression_ratio=0.3):
        self.max_context = max_context
        self.compression_ratio = compression_ratio
        self.memory_usage = 0
        self.compressed_fragments = []

    def compress(self, context):
        """
        Compress context with controlled loss
        """
        if self.memory_usage + len(context) > self.max_context:
            raise ValueError("Context exceeds maximum capacity")

        # Simulate compression by reducing dimensionality
        original_size = len(context)
        compressed_size = int(original_size * (1 - self.compression_ratio))
        compressed = context[:compressed_size]

        self.memory_usage += compressed_size
        self.compressed_fragments.append(compressed)
        return compressed

    def get_purity_score(self):
        """
        Estimate memory purity based on compression history
        """
        if not self.compressed_fragments:
            return 1.0  # Perfect purity with no fragments

        # Simple heuristic: higher compression ratio reduces purity
        purity = 1.0 - (self.compression_ratio * 0.7)
        return max(0.8, min(1.0, purity))  # Cap between 80-100%

    def clear(self):
        """
        Reset compressor state
        """
        self.memory_usage = 0
        self.compressed_fragments = []
