# Audit Tensor translations
import json

class AuditTensor:
    """Audit tensor translations for fidelity violations."""
    def __init__(self, tensor_store):
        self.tensor_store = tensor_store

    def check_fidelity(self, source_tensor, target_tensor, threshold=0.8):
        """Return True if similarity >= threshold.
        Uses cosine similarity of embedding vectors.
        """
        import numpy as np
        src = np.array(source_tensor['embedding'])
        tgt = np.array(target_tensor['embedding'])
        if src.size == 0 or tgt.size == 0:
            return False
        sim = np.dot(src, tgt) / (np.linalg.norm(src) * np.linalg.norm(tgt))
        return sim >= threshold

    def audit_all(self, threshold=0.8):
        """Audit all stored tensors against latest received tensors."""
        results = []
        for src_id, src_tensor in self.tensor_store.items():
            tgt_tensor = self.tensor_store.get(src_id)
            if tgt_tensor:
                ok = self.check_fidelity(src_tensor, tgt_tensor, threshold)
                results.append((src_id, ok))
        return results

# Example usage:
# store = {'t1': {'embedding': [0.1,0.2]}, 't2': {'embedding':[0.4,0.5]}}
# auditor = AuditTensor(store)
# print(auditor.audit_all())
