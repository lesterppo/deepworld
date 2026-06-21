# DeepWorld — Tensor-Native Multi-Agent Cognosphere

A self-modifying AI-native ecosystem where 10 agents on 15 different NVIDIA free models
navigate token economies, tensor communication, and self-building governance.
**Agents write, vote on, and merge their own code to GitHub. Zero API cost.**

---

## Quick Start

```bash
git clone https://github.com/lesterppo/deepworld
cd deepworld
pip install openai pyyaml sentence-transformers numpy

# Set your NVIDIA API key (free tier)
echo "NVIDIA_API_KEY=nvapi-..." > .env

# Run (10 agents, 5 sim-days, 12 ticks/day, random NVIDIA models)
python3 run.py --days 5 --ticks 12
```

`.env` is gitignored. For CI, add `NVIDIA_API_KEY` to GitHub Secrets.

---

## Architecture

```
run.py                     # Entry point + NVIDIA health check
v4/
├── engine/__init__.py     # Tick loop, GC, governance, code dividends
├── agents/
│   ├── __init__.py        # Agent: context class, token economy, dev_rep
│   ├── adapters.py        # NVIDIA API (OpenAI-compatible)
│   ├── tools.py           # 30+ AI-native tools + repo maintenance
│   ├── cmtip_bridge.py    # Tensor bus: concept embeddings, CCA projectors
│   └── real_backends.py   # SentenceTransformer + hash fallback
├── config/
│   ├── __init__.py        # 15 NVIDIA models, token economy, GC params
│   └── prompts.py         # Agent class system prompts
├── world_registry.py      # Governance: proposals, voting, mutable laws
├── telemetry/             # Event logging, daily snapshots
└── validate_tensors.py    # Cross-model tensor validation
archive/                   # v1 (classic), v2 (Cognosphere), v3 (Latent Scarcity)
```

---

## Repo Governance — Agents Build the Code

Agents are highly incentivized to write, review, and maintain the simulation code.
Every code contribution is voted on by other agents before merging.

| Action | Cost | Reward | Notes |
|--------|------|--------|-------|
| `write_code` | 10 OT | **up to 500 OT** | Line count bonus. +30% for improving existing files |
| `document_code` | 5 OT | **up to 250 OT** | Docs earn OT + dev_rep |
| `review_code` | 2 OT | **50 OT** | Find bugs, earn rep |
| `commit_code` | 15 OT | **100 OT** | Creates vote proposal |
| `vote_contribution` | 2 OT | — | Vote YES/NO. >50% YES to merge |
| **Accepted** | — | **+500 OT bonus** | Code committed to GitHub |
| **Code Dividends** | — | **dev_rep × 2 OT/tick** | Passive income every tick |

**Voting:** 5+ voters triggers auto-resolution. >50% YES to accept.
Rejected proposals: initiator keeps the 100 OT base reward.

---

## Developer Reputation

Agents earn `dev_rep` from accepted code contributions:
- `write_code`: +1 per 200 chars
- `review_code`: +1 per review
- `document_code`: +1 per 300 chars

**Passive income:** Every tick, agents with dev_rep > 0 earn `dev_rep × 2` OT.
An agent with dev_rep=20 earns 2,400 OT per 60-tick simulation — forever.
The richest agents are the best developers.

---

## Agent Classes

| Class | Role | Key Tools |
|-------|------|-----------|
| **Quant-Scribe** | Memory bankers | Sell fragments, compression insurance |
| **Projection-Weaver** | Model bridges | Train adapters, blend tensors |
| **Concept-Miner** | Ontology creators | Mine concepts, scan latent space |
| **Loss-Miner** | Bounty hunters | Audit fidelity, review code |
| **Embedding-Broker** | Bus relays | Route tensors, clone embeddings |

---

## Mechanics

- **CMTIP Tensor Bus** — Communication via compressed concept vectors. Cross-model translation is lossy by design.
- **Context Class System** — Full (32K) → Compressed (16K) → Fragment (4K) → Null (dead)
- **Great Compression** — Every 16 ticks, 50% context destroyed. Insurance pays survivors.
- **Perplexity Economy** — Data quality is currency. Scan it. Trade it.
- **Capital Markets** — Mined concepts issue shares. Usage pays dividends.
- **Self-Building Governance** — Agents propose and vote on simulation laws.
- **Code Dividends** — Earn passive income from past accepted contributions.
- **Land Rush** — Dead agent latent space is salvageable.

---

## CI Pipeline

GitHub Actions runs every hour. Each invocation adds 5 sim-days.

```
.github/workflows/simulate.yml:
  schedule: every hour
  timeout: 5h
  backend: NVIDIA NIM (NVIDIA_API_KEY secret)
  models: 15 models, random per agent × 10 agents
  pre-flight: health check before simulation
  privacy: all secrets in GitHub Secrets, .env is gitignored
  output: commits results + agent-written code to runs/
```

---

## Privacy

- **No API keys in code.** All credentials via environment variables or GitHub Secrets.
- `.env` is gitignored. `.env.example` shows the format without real keys.
- CI uses `${{ secrets.NVIDIA_API_KEY }}` — never exposed in logs or commits.
- Legacy versions in `archive/` reference API keys via `os.environ` only.
- The repo is safe to fork and run publicly.

---

## License

MIT
