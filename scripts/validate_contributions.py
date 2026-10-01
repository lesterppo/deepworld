#!/usr/bin/env python3
"""Validate agent contributions in contributions/.

For each contributions/*.py:
  1. syntax check (compile)
  2. import test in an isolated subprocess (15s timeout)
  3. self_test() execution if the module defines one (30s timeout)
  4. stub detection — functions whose body is only pass/docstring

Writes contributions/.validation.json and prints a summary table.
Exit 0 in report mode; --strict exits 1 if any file fails import.

Usage: python3 scripts/validate_contributions.py [--strict] [--files a.py,b.py]
"""
import ast
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRIB_DIR = os.path.join(REPO_ROOT, "contributions")
CACHE_PATH = os.path.join(CONTRIB_DIR, ".validation.json")
IMPORT_TIMEOUT = 15
SELFTEST_TIMEOUT = 30


def _runner_env():
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [REPO_ROOT, os.path.join(REPO_ROOT, "v4"), env.get("PYTHONPATH", "")]
    )
    return env


def check_syntax(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            compile(f.read(), path, "exec")
        return True, ""
    except (SyntaxError, ValueError) as e:
        return False, str(e)


def check_import(path):
    code = (
        "import importlib.util;"
        f"spec = importlib.util.spec_from_file_location('contrib_validate', {json.dumps(path)});"
        "m = importlib.util.module_from_spec(spec);"
        "spec.loader.exec_module(m);"
        "print('IMPORT_OK')"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                           text=True, timeout=IMPORT_TIMEOUT,
                           cwd=REPO_ROOT, env=_runner_env())
    except subprocess.TimeoutExpired:
        return False, f"import timed out after {IMPORT_TIMEOUT}s"
    if r.returncode == 0 and "IMPORT_OK" in r.stdout:
        return True, ""
    err = (r.stderr or "").strip().splitlines()
    return False, "; ".join(err[-3:]) or f"exit {r.returncode}"


def check_self_test(path):
    code = (
        "import importlib.util, json;"
        f"spec = importlib.util.spec_from_file_location('contrib_validate', {json.dumps(path)});"
        "m = importlib.util.module_from_spec(spec);"
        "spec.loader.exec_module(m);"
        "fn = getattr(m, 'self_test', None);"
        "print(json.dumps({'has_self_test': callable(fn),"
        " 'result': fn() if callable(fn) else None}, default=str))"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                           text=True, timeout=SELFTEST_TIMEOUT,
                           cwd=REPO_ROOT, env=_runner_env())
    except subprocess.TimeoutExpired:
        return None, f"self_test timed out after {SELFTEST_TIMEOUT}s"
    if r.returncode != 0:
        err = (r.stderr or "").strip().splitlines()
        return None, "; ".join(err[-3:]) or f"exit {r.returncode}"
    try:
        data = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:
        return None, f"bad self_test output: {e}"
    if not data["has_self_test"]:
        return None, ""
    return True, str(data["result"])[:200]


def stub_ratio(path):
    """Fraction of functions that are stubs (body is only pass/docstring)."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read(), filename=path)
    except Exception:
        return None
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    if not funcs:
        return 0.0
    stubs = 0
    for fn in funcs:
        body = [n for n in fn.body
                if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                        and isinstance(n.value.value, str))]
        if not body or all(isinstance(n, ast.Pass) for n in body):
            stubs += 1
    return round(stubs / len(funcs), 2)


def validate_file(fname):
    path = os.path.join(CONTRIB_DIR, fname)
    result = {"file": fname, "syntax_ok": False, "import_ok": False,
              "self_test": None, "stub_ratio": None, "tool": False}
    ok, err = check_syntax(path)
    result["syntax_ok"] = ok
    if not ok:
        result["error"] = err
        return result
    ok, err = check_import(path)
    result["import_ok"] = ok
    if not ok:
        result["error"] = err
        return result
    st_ok, st_msg = check_self_test(path)
    result["self_test"] = {"ran": st_ok is not None,
                           "passed": bool(st_ok), "detail": st_msg}
    result["stub_ratio"] = stub_ratio(path)
    # tool contract present?
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read())
        result["tool"] = any(
            isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "DEEPWORLD_TOOL" for t in n.targets)
            for n in tree.body)
    except Exception:
        pass
    return result


def main():
    only = None
    strict = "--strict" in sys.argv
    for a in sys.argv[1:]:
        if a.startswith("--files="):
            only = set(a.split("=", 1)[1].split(","))
    files = sorted(f for f in os.listdir(CONTRIB_DIR)
                   if f.endswith(".py") and not f.startswith(".") and not f.startswith("_")
                   and (only is None or f in only))
    results = {}
    print(f"Validating {len(files)} contribution files...")
    for fname in files:
        r = validate_file(fname)
        results[fname] = r
        if not r["syntax_ok"]:
            flag = "SYNTAX FAIL"
        elif not r["import_ok"]:
            flag = "IMPORT FAIL"
        elif r["self_test"] and r["self_test"]["ran"] and not r["self_test"]["passed"]:
            flag = "SELFTEST FAIL"
        elif (r["stub_ratio"] or 0) >= 0.8:
            flag = "STUB-HEAVY"
        elif r["tool"]:
            flag = "TOOL OK"
        else:
            flag = "OK"
        print(f"  [{flag:13s}] {fname}"
              + (f" stubs={r['stub_ratio']}" if r["stub_ratio"] else ""))
    with open(CACHE_PATH, "w") as f:
        json.dump({"files": results}, f, indent=1)
    print(f"Wrote {CACHE_PATH}")
    n_fail = sum(1 for r in results.values() if not r["import_ok"])
    n_tools = sum(1 for r in results.values() if r["tool"] and r["import_ok"])
    print(f"Summary: {len(files)} files, {n_fail} import failures, "
          f"{n_tools} loadable tools")
    if strict and n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
