"""Projection-Weaver adapter helper.

Extends the audit utilities with tensor fidelity checks
for cross-model projection monitoring.
"""
from audit_utils import scan_file

def check_projection_fidelity(adapter_name: str, fidelity: float) -> dict:
    """Check if a projection adapter meets quality thresholds."""
    status = "healthy" if fidelity >= 0.75 else "degraded" if fidelity >= 0.4 else "critical"
    return {
        "adapter": adapter_name,
        "fidelity": fidelity,
        "status": status,
        "recommendation": "retrain" if fidelity < 0.6 else "monitor",
    }

def scan_projection_adapters(base_dir: str = "v4/agents") -> list:
    """Scan for adapter definitions in the codebase."""
    import os
    results = []
    if os.path.isdir(base_dir):
        for root, dirs, files in os.walk(base_dir):
            for fn in files:
                if fn.endswith('.py'):
                    filepath = os.path.join(root, fn)
                    result = scan_file(filepath)
                    if result["imports"] > 3:
                        results.append({"file": fn, "imports": result["imports"]})
    return sorted(results, key=lambda r: -r["imports"])
