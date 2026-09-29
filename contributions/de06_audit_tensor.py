"""Audit Tensor Module

This module provides utilities to validate tensor fidelity across model families.
It includes:
- `compare_tensors` – compares a source tensor vector to a projected target
  and returns a fidelity score (0.0-1.0). The baseline fidelity is 0.2-0.4.
- `detect_fidelity_violation` – flags translations that fall below a threshold.
- `report_violation` – formats a report suitable for audit logs.

The code is intentionally lightweight to keep the cost low and to
serve as a foundation for future Loss‑Miner extensions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

# A simple vector type alias
Vector = List[float]

@dataclass
class FidelityResult:
    score: float
    passed: bool
    details: str

DEFAULT_BASELINE = 0.3
THRESHOLD = 0.25


def compare_tensors(source: Vector, target: Vector) -> float:
    """Return cosine similarity between two vectors.
    Both vectors are assumed to be already normalized.
    """
    if len(source) != len(target):
        raise ValueError("Vectors must be same length")
    dot = sum(a * b for a, b in zip(source, target))
    return max(0.0, min(1.0, dot))


def detect_fidelity_violation(source: Vector, target: Vector, baseline: float = DEFAULT_BASELINE) -> FidelityResult:
    """Detect if the fidelity between source and target is below the baseline.
    Returns a FidelityResult containing the score and a human‑readable message.
    """
    score = compare_tensors(source, target)
    passed = score >= baseline
    details = f"Fidelity {score:.3f} (baseline: {baseline:.3f})"
    return FidelityResult(score=score, passed=passed, details=details)


def report_violation(result: FidelityResult, source_id: str, target_id: str) -> str:
    """Generate a concise audit report.
    In a real audit, this would be logged or sent to a monitoring system.
    """
    status = "PASS" if result.passed else "FAIL"
    return (f"Audit Report – Source: {source_id}, Target: {target_id}
"
            f"Status: {status}
"
            f"Details: {result.details}
")

# Example usage (for quick manual tests)
if __name__ == "__main__":
    # Normalized dummy vectors
    src = [0.6, 0.8]
    tgt = [0.6, 0.8]  # identical
    res = detect_fidelity_violation(src, tgt)
    print(report_violation(res, "src_vec", "tgt_vec"))
