# DeepWorld v5 — Development Guide

AI-native multi-agent tensor simulation. Agents navigate token economies,
context windows, and cross-model semantic decay via CMTIP tensor bus.

**Archived:** v1 (classic sandbox), v2 (Cognosphere), v3 (Latent Scarcity) → `archive/`

---

## Quick Start (Hermes Agents)

```bash
git clone https://github.com/lesterppo/deepworld
cd deepworld
pip install openai pyyaml sentence-transformers numpy

# NVIDIA-only (default, free tier)
python3 run.py --days 3 --ticks 8

# CI continuous mode
python3 run.py --days 5 --ticks 12 --delay 0.1 --output runs
```

---

## Key Finding

**15 different models on the same NVIDIA backend produce different agent behaviors.**
Model diversity IS the simulation mechanic — different architectures (Llama, Gemma,
Mistral, Qwen, Phi, DeepSeek, GPT-OSS) interpret the same tensor differently due
to cross-model semantic decay.

---

## File Structure

```
run.py                      # Root entry point + NVIDIA health check
v4/
├── engine/__init__.py      # OmniTokV4Engine: tick loop, GC, governance, CMTIP
├── agents/
│   ├── __init__.py         # OmniTokV4Agent: context class, token economy, tensors
│   ├── adapters.py         # MultiModelAdapter: NVIDIA API (OpenAI-compatible)
│   ├── tools.py            # 30+ AI-native tools (send_tensor, mine_concept, etc.)
│   ├── cmtip_bridge.py     # CMTIP tensor bus: concept embeddings, CCA projectors
│   └── real_backends.py    # SentenceTransformer + deterministic hash fallback
├── config/
│   ├── __init__.py         # NVIDIA_FREE_MODELS (15 models), token economy params
│   └── prompts.py          # 5 agent class system prompts
├── world_registry.py       # Self-building governance: proposals, voting, laws
├── telemetry/__init__.py   # OmniObserverV4: event logging, daily snapshots
└── validate_tensors.py     # Cross-model tensor validation suite
runs/                       # Simulation output (committed by CI)
archive/                    # v1, v2, v3 (preserved, not active)
```

---

## NVIDIA Model Pool (15 models)

Each agent randomly assigned from:
- `nvidia/llama-3.1-nemotron-nano-8b-v1` — Fast
- `nvidia/llama-3.1-nemotron-51b-instruct` — Balanced
- `nvidia/llama-3.1-nemotron-70b-instruct` — Large
- `nvidia/llama-3.3-nemotron-super-49b-v1` — Super
- `nvidia/llama-3.3-nemotron-super-49b-v1.5` — Super v1.5
- `meta/llama-4-maverick-17b-128e-instruct` — Llama 4
- `meta/llama-3.1-8b-instruct` — Classic
- `google/gemma-3-12b-it` — Gemma 3
- `mistralai/mistral-nemotron` — Mistral
- `nvidia/nemotron-4-340b-instruct` — Massive
- `openai/gpt-oss-20b` — GPT-OSS
- `qwen/qwen3.5-122b-a10b` — Qwen MoE
- `deepseek-ai/deepseek-v4-flash` — DeepSeek
- `microsoft/phi-4-mini-instruct` — Phi-4
- `nvidia/nemotron-3-super-120b-a12b` — Nemotron 3

All through `https://integrate.api.nvidia.com/v1` (OpenAI-compatible).

---

## How to Extend

**Add a new NVIDIA model:**
1. Add to `NVIDIA_FREE_MODELS` in `v4/config/__init__.py`

**Add a new agent class:**
1. `v4/config/prompts.py` — add class prompt
2. `v4/config/__init__.py` — add to `AGENT_CLASSES`
3. `v4/agents/tools.py` — add class-specific tools

**Add a new mechanic:**
1. `v4/config/__init__.py` — add constants
2. `v4/agents/__init__.py` — add to `apply_effects()`
3. `v4/engine/__init__.py` — add trigger in `tick()`
4. `v4/telemetry/__init__.py` — add tracking metric

---

## CI Pipeline

```
.github/workflows/simulate.yml:
  schedule: every 2h
  timeout: 5h
  backend: NVIDIA NIM (NVIDIA_API_KEY secret)
  models: 15 models, random per agent × 10 agents
  pre-flight: health check validates API before simulation
  output: commits to runs/
  state: .world_state.json persists governance
```

**Setup:** Add `NVIDIA_API_KEY` to GitHub Secrets → Enable Actions.

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `self.tick` shadows method | Use `self.current_tick` |
| CMTIP requires `sentence-transformers` | Falls back to deterministic hash embeddings if unavailable |
| NVIDIA models have different context windows | Handled by `MODEL_BACKENDS` context_limit per family |
| `.world_state.json` grows with governance events | Truncated to last 50 events on save |
| Agent dies silently | Check `death_cause` in telemetry; most common: `token_exhaustion`, `context_collapse` |

---

## Design Philosophy

- **Mechanics > narrative.** Context class mobility, perplexity markets, and CMTIP tensor drift emerge from rules.
- **Model diversity IS the simulation.** 15 models interpret the same concept differently.
- **Tensors are cheap, text is bankruptcy.** `send_tensor` costs 2 OT. `transmit_message` costs 50 OT.
- **The world builds itself.** Agents propose and vote on rule changes through governance.
