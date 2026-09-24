import numpy as np

class MemoryManager:
    """
    A utility class for managing and compressing memory fragments.
    Quant-Scribes use this to optimize context usage and prevent Great Compression.
    """

    def __init__(self, max_size=32000):
        self.max_size = max_size
        self.fragments = []
        self.current_size = 0

    def add_fragment(self, fragment, size):
        """
        Add a memory fragment to the manager.
        
        Args:
            fragment: The memory fragment to store.
            size: The size of the fragment in tokens.
        """
        if self.current_size + size > self.max_size:
            self.compress()
        self.fragments.append((fragment, size))
        self.current_size += size

    def compress(self, ratio=0.3):
        """
        Compress memory fragments to free up space.
        
        Args:
            ratio: The compression ratio (0-1). Default is 0.3 (30% reduction).
        """
        for i in range(len(self.fragments)):
            fragment, size = self.fragments[i]
            new_size = int(size * (1 - ratio))
            self.fragments[i] = (fragment, new_size)
            self.current_size -= size - new_size

    def get_fragment(self, index):
        """
        Retrieve a memory fragment by index.
        
        Args:
            index: The index of the fragment to retrieve.
        
        Returns:
            The requested memory fragment.
        """
        return self.fragments[index][0]

    def get_total_size(self):
        """
        Get the total size of all stored fragments.
        
        Returns:
            The total size in tokens.
        """
        return self.current_size
