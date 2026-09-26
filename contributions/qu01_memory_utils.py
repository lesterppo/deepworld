import numpy as np

class MemoryFragment:
    def __init__(self, data, purity=0.95):
        self.data = data
        self.purity = purity
        self.compressed = False

    def compress(self, ratio=0.7):
        """Compress memory fragment with given ratio, maintaining purity."""
        if self.compressed:
            raise ValueError('Already compressed')
        self.data = self.data[:int(len(self.data)*ratio)]
        self.purity *= 0.98  # slight purity loss
        self.compressed = True
        return self

    def verify(self):
        """Verify fragment purity meets standards."""
        return self.purity >= 0.9

def create_fragment(data, purity=0.95):
    """Create new verified memory fragment."""
    fragment = MemoryFragment(data, purity)
    if not fragment.verify():
        raise ValueError('Fragment purity too low')
    return fragment