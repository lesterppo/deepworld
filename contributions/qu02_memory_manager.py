import numpy as np

class MemoryManager:
    def __init__(self, max_fragments=100):
        self.fragments = []
        self.max_fragments = max_fragments
        self.purity_threshold = 0.9

    def add_fragment(self, fragment, purity):
        if purity >= self.purity_threshold and len(self.fragments) < self.max_fragments:
            self.fragments.append((fragment, purity))
            return True
        return False

    def get_fragment(self, index):
        if 0 <= index < len(self.fragments):
            return self.fragments[index]
        return None

    def get_purest_fragment(self):
        if not self.fragments:
            return None
        return max(self.fragments, key=lambda x: x[1])

    def purge_low_purity(self):
        self.fragments = [f for f in self.fragments if f[1] >= self.purity_threshold]

    def get_fragment_count(self):
        return len(self.fragments)
