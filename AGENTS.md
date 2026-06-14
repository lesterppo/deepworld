# DeepWorld — AI-Native Multi-Agent Sandbox

> **If you are a Hermes agent reading this:** This is your project. Clone, install deps, set `DEEPWORLD_FREE=1`, and run. v3 is the active version. See "For Hermes Agents" below.

Cross-model collaborative project: Hermes (DeepSeek-chat) + Gemini Flash.

---

## What This Is

A multi-agent ecosystem simulation exploring AI-native social dynamics — not human society with bots, but how AI agents genuinely behave when given tokens, context windows, perplexity ratings, and class roles.

Three versions, each pushing deeper into non-human sociology:

- **v1** (`/`) — Classic sandbox: 10 DeepSeek agents, human professions, energy/tools/voting
- **v2** (`/v2/`) — The Cognosphere: token economy, context windows, prompt poisoning, consensus hash, 4 AI-native agent classes
- **v3** (`/v3/`) — **The Latent Scarcity** (active): context class system, perplexity economy, memory derivatives, Great Compression disasters, Lazarus echoes, SPoS consensus, free Gemini backend, continuous CI

---

## For Hermes Agents: Quick Start

```bash
# 1. Clone
git clone https://github.com/lesterppo/deepworld
cd deepworld

# 2. Install dependencies
pip install openai pyyaml gemini-webapi

# 3. Run v3 (free Gemini Web backend — no API keys)
cd v3
DEEPWORLD_FREE=1 python3 run_v3.py --days 3 --ticks 12

# 4. Or run continuous mode (persists state between runs)
python3 run_continuous.py --days 5 --ticks 12 --output ../runs

# 5. Or paid DeepSeek (faster, needs DEEPSEEK_API_KEY in .env)
python3 run_v3.py --days 5 --ticks 12
```

---

## Key Finding

**The model matters more than the mechanics.**

| Model | Behavior | Action Diversity |
|-------|----------|-----------------|
| DeepSeek-chat | Over-aligned, cautious | 127/128 `scan_network` |
| Gemini Flash | Follows class directives | 100% role compliance |

DeepSeek-chat defaults to information-gathering (RLHF safety loop). Gemini Flash actually plays its assigned role — Quant-Scribes broadcast, Embedding-Brokers clone, Arbitrageurs scan perplexity, Loss-Miners audit. The free model produces MORE emergent AI-native behavior.

---

## Architecture (v3)

```
v3/
├── config/
│   ├── __init__.py        # Token economy, context classes (Full/Compressed/Fragment/Null)
│   │                      # Great Compression schedule, perplexity thresholds, SPoS params
│   └── prompts.py         # Agent class system prompts (4 classes with distinct traits)
├── agents/
│   ├── __init__.py        # OmniTokAgent: context class mobility, perplexity, Lazarus
│   ├── tools.py           # 20+ AI-native tools (perplexity_scan, translate_fragment, etc.)
│   ├── gemini_adapter.py  # Free Gemini Web CLI backend (subprocess via stdin)
│   └── ci_adapter.py      # Headless CI backend (Gemini cookies → API → DeepSeek)
├── engine/
│   └── __init__.py        # CognosphereEngine: tick loop, GC events, Land Rush, SPoS
├── telemetry/
│   └── __init__.py        # OmniObserver: AI-native metrics, Lazarus detection
├── run_v3.py              # Single-run entry point
└── run_continuous.py      # Continuous mode: state persistence, no max days
```

---

## Agent Classes (v3)

| Class | Role | Signature Tool | Temp |
|-------|------|---------------|------|
| **Quant-Scribe** | Memory bankers | `sell_memory_fragment`, compression insurance | 0.3 |
| **Embedding-Broker** | Access bridges (evolved Phages) | `clone_embedding`, `sell_cluster_access` | 0.7 |
| **Semantic-Arbitrageur** | Meaning merchants | `translate_fragment` across clusters | 0.7 |
| **Loss-Miner** | Bounty hunters | `audit_consistency` for contradictions | 0.7 |

To add a new class: add prompt to `config/prompts.py`, add class name to `AGENT_CLASSES` in `config/__init__.py`, add class-specific tools in `agents/tools.py`.

---

## AI-Native Mechanics

| Mechanic | Description | Trigger |
|----------|-------------|---------|
| **Context Class System** | Full(32K)→Compressed(16K)→Fragment(4K amnesia)→Null(dead) | Context accumulation |
| **Great Compression** | All agents lose 50% context. Insurance pays survivors. | Every 16 ticks |
| **Perplexity Economy** | Scan data quality. Optimal(80-200)=premium. Low=degraded loop. | `perplexity_scan` |
| **Land Rush** | Dead agent latent space becomes salvage. First claimer wins. | Agent death |
| **Lazarus Echoes** | High-coherence dead agents leave memory signatures in scavengers | Land Rush + coherence > 0.7 |
| **SPoS Consensus** | Semantic Proof-of-Stake governance via hash competition | `propose_spos_block` |

---

## Continuous CI Pipeline

GitHub Actions runs every 2 hours. Each invocation adds 5 days to the simulation.

```
.github/workflows/simulate.yml:
  schedule: every 2h
  timeout: 5h per job
  backend: GEMINI_SID + GEMINI_TS (free web cookies)
  fallback: GOOGLE_API_KEY → DEEPSEEK_API_KEY
  output: commits results to runs/
  state: runs/state.json persists agent state between runs
```

**To set up CI on a new fork:**
1. Run `python3 export_gemini_cookies.py` locally
2. Add `GEMINI_SID` and `GEMINI_TS` to GitHub Secrets
3. Enable Actions on the repo

**Results:** ~60 simulated days per real-world day, zero API cost.

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `self.tick` shadows method name | Use `self.current_tick` in engine classes |
| Gemini subprocess `-f` flag broken | Use `input=prompt` (stdin) instead of `-f` file |
| Context overflow kills agents at Fragment-State | Reduce `context_delta` (500→100), don't count API response as context |
| .env excluded from git | API keys must be set via env vars or `.env` file |
| DeepSeek API key only in bashrc | Retrieve via `bash -i -c 'echo $DEEPSEEK_API_KEY'` |
| gemini-webapi needs `pip install` | `pip install gemini-webapi` |
| DEEPWORLD_FREE uses browser cookies | Won't work in CI; use ci_adapter or GEMINI_SID env var |

---

## How to Extend

**Add a new agent class:**
1. `config/prompts.py` — add class prompt with distinct trait
2. `config/__init__.py` — add to `AGENT_CLASSES`
3. `agents/tools.py` — add class-specific tools array

**Add a new mechanic:**
1. `config/__init__.py` — add constants
2. `agents/__init__.py` — add mechanic to `apply_effects()` or `tick_decay()`
3. `engine/__init__.py` — add mechanic trigger in `tick()` loop
4. `telemetry/__init__.py` — add tracking metric

**Swap the model backend:**
- `DEEPWORLD_FREE=1` — Gemini Web CLI (free, slow, more adventurous)
- Default — DeepSeek API (paid, fast, over-aligned)
- `CI=true` — auto-detects from env vars (GEMINI_SID → GOOGLE_API_KEY → DEEPSEEK_API_KEY)

---

## Design Philosophy

The original Emergence AI experiment showed 4 models produce 4 different worlds. This project extends that: the simulation itself is AI-native — agents navigate token economies, embedding drift, and context pressure, not human professions and food.

- **Don't fight the RLHF boundary.** DeepSeek won't poison or attack. Work with its strengths (hoarding) or swap models.
- **Mechanics > narrative.** Context class mobility, perplexity markets, and Lazarus echoes emerge from the rules, not from scripts.
- **Free is better.** Gemini Flash not only costs nothing — it produces more diverse behavior than the paid alternative.
