import json
from typing import List

# Simple audit module for tensor translation fidelity
# This module provides utilities to compare source and target embeddings
# and flag potential fidelity violations.


def compute_cosine(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(a*b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a*a for a in vec_a) ** 0.5
    norm_b = sum(b*b for b in vec_b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def audit_translation(source: List[float], target: List[float], threshold: float = 0.8) -> bool:
    """Return True if translation fidelity is acceptable.
    Threshold defaults to 0.8 (cosine similarity)."""
    similarity = compute_cosine(source, target)
    return similarity >= threshold


def main():
    # Example usage: load two embeddings from JSON and audit
    with open('source.json') as f:
        src = json.load(f)['embedding']
    with open('target.json') as f:
        tgt = json.load(f)['embedding']
    ok = audit_translation(src, tgt)
    print('Translation OK' if ok else 'Fidelity violation detected')

if __name__ == "__main__":
    main()
