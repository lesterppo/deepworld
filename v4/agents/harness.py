"""
DeepWorld v5.x — agent harness mechanisms (vendored).

Provenance: ported from lesterppo/arxiv-lab (src/arxiv_lab/harness/),
which implements the three representative mechanisms of Mingbird, a
local-first agent harness for small open models (arXiv:2610.02001).
Validated: CPU toy-env (all checks passed) + gpt-oss-20b via NVIDIA NIM.

  PrefillBudget  — byte-level net-zero prefill budget. Tool prefill that
                   overflows the budget is compressed (descriptions, then
                   examples dropped) so the marginal prefill cost stays flat.
  LoopDetector   — signature-level loop detection. Fingerprints each action
                   as (tool, canonical args); a repeated signature or
                   repeated short cycle halts the step-burn.
  FinishGate     — re-reads the task before accepting a 'done' claim; every
                   success criterion is re-checked against live state.
                   (Available for task-style flows; the tick loop has no
                   task-completion primitive, so it is not wired there.)

Tuning via env:
  DEEPWORLD_PREFILL_BUDGET  byte budget for injected tool text (default 8000)
  DEEPWORLD_LOOPDETECT      1 to enable loop breaking in act() (default 1)
  DEEPWORLD_LOOP_K          repeat threshold (default 4)
"""

import hashlib
import json
import os


class PrefillBudget:
    """Enforce a byte budget on harness prefill."""

    def __init__(self, budget_bytes: int):
        self.budget_bytes = budget_bytes

    @staticmethod
    def _schema_bytes(schema: dict, level: int) -> str:
        d = dict(schema)
        if level >= 1:
            d.pop("examples", None)
            d.get("parameters", {}).pop("examples", None)
        if level >= 2:
            d.pop("description", None)
        return json.dumps(d, separators=(",", ":"))

    def build_prefill(self, system_text: str, tool_schemas: list):
        """Fit (system_text + tool schemas) into the budget, compressing
        schemas level by level. Returns (text, bytes_used, compressed)."""
        parts = [system_text] + [self._schema_bytes(s, 0) for s in tool_schemas]
        blob = "\n".join(parts).encode("utf-8")
        if len(blob) <= self.budget_bytes:
            return blob.decode("utf-8"), len(blob), False
        for level in (1, 2):
            parts = [system_text] + [self._schema_bytes(s, level)
                                     for s in tool_schemas]
            blob = "\n".join(parts).encode("utf-8")
            if len(blob) <= self.budget_bytes:
                return blob.decode("utf-8"), len(blob), True
        head = system_text.encode("utf-8")[: self.budget_bytes // 2]
        rest = b"\n".join(self._schema_bytes(s, 2).encode("utf-8")
                          for s in tool_schemas)
        blob = (head + b"\n" + rest)[: self.budget_bytes]
        return blob.decode("utf-8", "ignore"), len(blob), True

    def fit_lines(self, lines: list, priority_names: frozenset = frozenset()):
        """Fit compact '  - name(params): desc' tool lines into the budget.

        Pass 1: strip per-line descriptions (keep name+params). Pass 2: drop
        lowest-priority whole lines (priority_names kept longest).
        Returns (text, bytes_used, compressed)."""
        def join(ls):
            return "\n".join(ls)
        blob = join(lines).encode("utf-8")
        if len(blob) <= self.budget_bytes:
            return join(lines), len(blob), False
        stripped = [ln.split(": ", 1)[0] if ": " in ln else ln for ln in lines]
        blob = join(stripped).encode("utf-8")
        if len(blob) <= self.budget_bytes:
            return join(stripped), len(blob), True
        ordered = sorted(range(len(stripped)),
                         key=lambda i: (0 if any(p in stripped[i]
                                                 for p in priority_names) else 1, -i))
        keep = set(ordered)
        cur = list(stripped)
        while keep:
            # drop one lowest-priority line at a time (from the end)
            drop = max(keep - {i for i in keep
                               if any(p in stripped[i] for p in priority_names)}
                       or keep)
            keep.discard(drop)
            cur = [stripped[i] for i in sorted(keep)]
            blob = join(cur).encode("utf-8")
            if len(blob) <= self.budget_bytes:
                return join(cur), len(blob), True
        return "", 0, True


class FinishGate:
    """Re-read the task before accepting completion. criteria: list of
    (name, check_fn(state) -> bool). review() returns (accepted, failed)."""

    def __init__(self, task_text: str, criteria: list):
        self.task_text = task_text
        self.criteria = criteria

    def review(self, state) -> tuple:
        failed = [name for name, check in self.criteria if not check(state)]
        return (len(failed) == 0), failed


class LoopDetector:
    """Signature-level loop detection over (tool, canonical args)."""

    def __init__(self, repeat_k: int = 4, max_cycle: int = 4):
        self.repeat_k = repeat_k
        self.max_cycle = max_cycle
        self.history = []

    @staticmethod
    def signature(tool: str, args: dict) -> str:
        canon = json.dumps(args, sort_keys=True, separators=(",", ":"),
                           default=str)
        return hashlib.sha1(f"{tool}|{canon}".encode()).hexdigest()[:12]

    def observe(self, tool: str, args: dict):
        sig = self.signature(tool, args)
        self.history.append(sig)
        h = self.history
        if len(h) >= self.repeat_k and len(set(h[-self.repeat_k:])) == 1:
            return f"loop: signature {sig} repeated {self.repeat_k}x"
        for cyc in range(2, self.max_cycle + 1):
            if len(h) >= 2 * cyc and h[-2 * cyc:-cyc] == h[-cyc:]:
                return f"loop: {cyc}-step cycle repeated"
        return None

    def reset(self):
        self.history = []


def prefill_budget_bytes() -> int:
    return int(os.environ.get("DEEPWORLD_PREFILL_BUDGET", "8000"))


def loopdetect_enabled() -> bool:
    return os.environ.get("DEEPWORLD_LOOPDETECT", "1") == "1"


def loopdetect_k() -> int:
    return int(os.environ.get("DEEPWORLD_LOOP_K", "4"))
