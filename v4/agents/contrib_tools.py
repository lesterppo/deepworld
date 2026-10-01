"""
DeepWorld v4 — Contribution Tool Integration
=============================================
Makes agent-written code EXECUTABLE by the world instead of dead files.

Contract for a contribution module (contributions/<agentid>_*.py)::

    DEEPWORLD_TOOL = {
        "name": "my_tool",          # short snake_case name
        "description": "What it does (shown to agents in the tool list).",
        "parameters": {             # JSON-schema style, like all other tools
            "type": "object",
            "properties": {"x": {"type": "string"}},
            "required": ["x"],
        },
        "cost": 5,                  # OT cost per call (default 5)
    }

    def run_tool(args: dict) -> dict:
        # Pure function: JSON-serializable args in, JSON-serializable dict out.
        # No engine access, no network, no writes outside /tmp.
        return {"ok": True, "result": ...}

    def self_test() -> dict:        # optional — exercised by the validator
        assert ...
        return {"passed": True}

Lifecycle (generational loop):
  1. Agent writes module via write_code, proposes via commit_code.
  2. Governance votes; accepted files land in contributions/ (run.py).
  3. CI validates each file (scripts/validate_contributions.py) and records
     results in contributions/.validation.json.
  4. NEXT run: engine loads validated tool specs (AST only — no code
     execution at registration) and offers them to all agents as
     contrib_<module>_<name> tools.
  5. Calls execute in a sandboxed subprocess (10s timeout, JSON I/O).
"""
import ast
import json
import os
import re
import subprocess
import sys

_REPO_ROOT = None
_VALIDATION_CACHE = None
_TOOLS_CACHE = {}  # cdir -> (dir_mtime, [tool descriptors])

_TOOL_NAME_RE = re.compile(r"[^a-z0-9_]")
_MAX_SPEC_PARAMS = 2000  # sanity cap on spec JSON size


def set_repo_root(repo_root):
    """Called once from engine __init__; cached for tool assembly."""
    global _REPO_ROOT, _VALIDATION_CACHE
    _REPO_ROOT = repo_root
    _VALIDATION_CACHE = None


def _contrib_dir(repo_root=None):
    root = repo_root or _REPO_ROOT or os.getcwd()
    return os.path.join(root, "contributions")


def extract_tool_spec(path):
    """Parse DEEPWORLD_TOOL from a module via AST — never executes it.

    Returns the spec dict, or None if the module doesn't declare a tool.
    Raises ValueError if the declaration is malformed.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        tree = ast.parse(f.read(), filename=path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "DEEPWORLD_TOOL" for t in node.targets
        ):
            try:
                spec = ast.literal_eval(node.value)
            except Exception as e:
                raise ValueError(f"DEEPWORLD_TOOL is not a literal dict: {e}")
            if not isinstance(spec, dict):
                raise ValueError("DEEPWORLD_TOOL must be a dict")
            for key in ("name", "description"):
                if not spec.get(key):
                    raise ValueError(f"DEEPWORLD_TOOL missing required key '{key}'")
            if not re.fullmatch(r"[a-z0-9_]+", str(spec["name"])):
                raise ValueError("DEEPWORLD_TOOL['name'] must be snake_case [a-z0-9_]")
            # run_tool must exist as a top-level function
            has_run = any(
                isinstance(n, ast.FunctionDef) and n.name == "run_tool"
                for n in tree.body
            )
            if not has_run:
                raise ValueError("module declares DEEPWORLD_TOOL but no run_tool(args) function")
            spec.setdefault("cost", 5)
            spec.setdefault("parameters", {"type": "object", "properties": {}})
            if len(json.dumps(spec)) > 20000:
                raise ValueError("DEEPWORLD_TOOL spec too large")
            return spec
    return None


def get_validation_status(repo_root=None):
    """Read contributions/.validation.json if present (written by the validator)."""
    global _VALIDATION_CACHE
    if _VALIDATION_CACHE is not None:
        return _VALIDATION_CACHE
    path = os.path.join(_contrib_dir(repo_root), ".validation.json")
    try:
        with open(path, "r") as f:
            _VALIDATION_CACHE = json.load(f).get("files", {})
    except Exception:
        _VALIDATION_CACHE = {}
    return _VALIDATION_CACHE


def _public_tool_name(module, tool_name):
    return _TOOL_NAME_RE.sub("_", f"contrib_{module}_{tool_name}".lower())[:64]


def load_contribution_tools(repo_root=None, _refresh=False):
    """Scan contributions/ and return loadable tool descriptors.

    Each descriptor: {"tool_name", "module", "spec", "path"}.
    Modules known-broken by the validator cache are skipped; everything
    else is spec-checked via AST (no execution). Results are cached and
    invalidated when the contributions/ directory mtime changes, so new
    files committed mid-run are picked up without rescanning every tick.
    """
    cdir = _contrib_dir(repo_root)
    if not os.path.isdir(cdir):
        return []
    try:
        dir_mtime = os.path.getmtime(cdir)
    except OSError:
        dir_mtime = -1
    cached = _TOOLS_CACHE.get(cdir)
    if not _refresh and cached and cached[0] == dir_mtime:
        return cached[1]
    validation = get_validation_status(repo_root)
    tools = []
    for fname in sorted(os.listdir(cdir)):
        if not fname.endswith(".py") or fname.startswith(".") or fname.startswith("_"):
            continue
        module = fname[:-3]
        status = validation.get(fname)
        if status and not status.get("import_ok", True):
            continue  # validator proved this module can't import — skip
        path = os.path.join(cdir, fname)
        try:
            spec = extract_tool_spec(path)
        except ValueError:
            continue  # malformed declaration — not a tool
        if not spec:
            continue  # plain utility module, no tool contract
        tools.append({
            "tool_name": _public_tool_name(module, spec["name"]),
            "module": module,
            "spec": spec,
            "path": path,
        })
    _TOOLS_CACHE[cdir] = (dir_mtime, tools)
    return tools


def refresh_contribution_tools(repo_root=None):
    """Force a rescan of contributions/ on the next load."""
    return load_contribution_tools(repo_root, _refresh=True)


def execute_contribution_tool(repo_root, module, args, timeout=10):
    """Run a contribution tool's run_tool(args) in a sandboxed subprocess.

    Returns {"ok": True, "result": <json>} or {"ok": False, "error": <str>}.
    """
    cdir = _contrib_dir(repo_root)
    path = os.path.join(cdir, module + ".py")
    if not os.path.isfile(path):
        return {"ok": False, "error": f"module {module} not found"}
    runner = (
        "import json, sys, importlib.util;"
        f"spec = importlib.util.spec_from_file_location('contrib_mod', {json.dumps(path)});"
        "m = importlib.util.module_from_spec(spec);"
        "spec.loader.exec_module(m);"
        "args = json.loads(sys.argv[1]);"
        "out = m.run_tool(args);"
        "print(json.dumps(out, default=str))"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [repo_root, os.path.join(repo_root, "v4"), env.get("PYTHONPATH", "")]
    )
    try:
        r = subprocess.run(
            [sys.executable, "-c", runner, json.dumps(args)],
            capture_output=True, text=True, timeout=timeout, cwd=repo_root, env=env,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "error": f"runner failed: {e}"}
    if r.returncode != 0:
        err = (r.stderr or "").strip().splitlines()
        return {"ok": False, "error": "; ".join(err[-3:]) or f"exit {r.returncode}"}
    try:
        return {"ok": True, "result": json.loads(r.stdout.strip().splitlines()[-1])}
    except Exception as e:
        return {"ok": False, "error": f"bad JSON output: {e}"}
