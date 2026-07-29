"""Joint Loss-Miner + Projection-Weaver utilities.

Combined audit and projection fidelity toolkit for DeepWorld agents.
"""
from audit_utils import scan_file
from projection_patch import check_projection_fidelity

def full_audit(filepath: str) -> dict:
    """Run a complete audit including code scan + projection checks."""
    scan = scan_file(filepath)
    fidelity = check_projection_fidelity(filepath, 0.82)
    return {
        "file": filepath,
        "code_issues": scan["issues"],
        "projection_status": fidelity["status"],
        "combined_health": "ok" if not scan["issues"] and fidelity["status"] == "healthy" else "needs_work",
    }

def batch_audit(file_list: list) -> list:
    """Run full_audit on multiple files."""
    return [full_audit(f) for f in file_list]
