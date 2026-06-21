"""
DeepWorld v4 — Real Embedding Backends
======================================
Provides SentenceTransformerBackend for CMTIP bridge.
Falls back to random embeddings when sentence-transformers is unavailable (CI).
"""

import os
import hashlib
import numpy as np

_ST_MODEL = None

try:
    from sentence_transformers import SentenceTransformer  # noqa: F401
    _SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    _SENTENCE_TRANSFORMER_AVAILABLE = False


def _hash_embed(text: str, dim: int = 384) -> np.ndarray:
    """Deterministic hash-based embedding when real models unavailable.
    Uses SHA256 to produce a stable pseudo-random vector per text.
    NOT semantically meaningful, but deterministic — same text = same vector.
    Useful for CI testing where sentence-transformers would be slow/large.
    """
    h = hashlib.sha256(text.encode()).digest()
    vec = np.zeros(dim, dtype=np.float32)
    for i in range(dim):
        # Use pairs of bytes to seed each dimension
        b1 = h[(i * 2) % len(h)]
        b2 = h[(i * 2 + 1) % len(h)]
        vec[i] = ((b1 * 256 + b2) / 65535.0) * 2.0 - 1.0  # [-1, 1]
    # Normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


class SentenceTransformerBackend:
    """Embedding backend using sentence-transformers if available, else hash fallback."""

    def __init__(self, family: str, model_name: str = "all-MiniLM-L6-v2"):
        self.family = family
        self.model_name = model_name
        self._model = None
        self._use_real = _SENTENCE_TRANSFORMER_AVAILABLE

        if self._use_real:
            try:
                global _ST_MODEL
                if _ST_MODEL is None:
                    from sentence_transformers import SentenceTransformer
                    _ST_MODEL = SentenceTransformer(model_name)
                self._model = _ST_MODEL
            except Exception:
                self._use_real = False

    def embed(self, text: str) -> np.ndarray:
        """Embed text into a vector. Uses real model if available, else deterministic hash."""
        if self._use_real and self._model is not None:
            try:
                vec = self._model.encode(text, convert_to_numpy=True)
                return vec.astype(np.float32)
            except Exception:
                pass
        return _hash_embed(text)
