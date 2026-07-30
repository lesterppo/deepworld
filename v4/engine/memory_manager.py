import numpy as np

class MemoryManager:
    def __init__(self, max_tokens=32000):
        self.max_tokens = max_tokens
        self.memory = []
        self.compression_ratio = 0.7

    def add_memory(self, content: str, tokens: int = 0) -> bool:
        """Add new content to memory, compressing if necessary"""
        if tokens == 0:
            tokens = len(content.split())

        if self.get_token_count() + tokens > self.max_tokens:
            self.compress_memory()

        self.memory.append(content)
        return True

    def get_token_count(self) -> int:
        """Calculate current token usage"""
        return sum(len(item.split()) for item in self.memory)

    def compress_memory(self) -> None:
        """Compress memory by retaining only key information"""
        if not self.memory:
            return

        # Simple compression: keep only the most recent important fragments
        self.memory = self.memory[int(len(self.memory) * (1 - self.compression_ratio)):]
        # More sophisticated compression could be implemented here

    def clear_memory(self) -> None:
        """Clear all memory"""
        self.memory = []

    def get_compressed_content(self) -> str:
        """Return the compressed content as a single string"""
        return '\n'.join(self.memory)
