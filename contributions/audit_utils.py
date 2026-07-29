"""Loss-Miner audit utilities for code review.

Provides scanning functions for common code issues
that Loss-Miner agents use during review_code calls.
"""
import os
import re

def scan_file(filepath: str) -> dict:
    """Scan a file and return issues found."""
    if not os.path.exists(filepath):
        return {"status": "missing", "issues": []}
    with open(filepath) as f:
        content = f.read()
    issues = []
    if "TODO" in content:
        issues.append("has TODOs")
    if "FIXME" in content:
        issues.append("has FIXMEs")
    if "print(" in content:
        issues.append("has debug prints")
    imports = len(re.findall(r'^import |^from ', content, re.MULTILINE))
    return {
        "status": "ok",
        "issues": issues,
        "lines": len(content.splitlines()),
        "imports": imports,
    }
