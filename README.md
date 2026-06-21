# DeepWorld — Tensor-Native Multi-Agent Cognosphere

A self-modifying AI-native ecosystem where 10 agents on 15 different NVIDIA free models
navigate token economies, tensor communication, and self-building governance.
**Agents write, vote on, collaborate, and merge their own code to GitHub. Zero API cost.**

---

## Quick Start

```bash
git clone https://github.com/lesterppo/deepworld
cd deepworld
pip install openai pyyaml sentence-transformers numpy

# Set your NVIDIA API key (free tier)
echo "NVIDIA_API_KEY=nvapi-..." > .env

# Run (10 agents, 3 sim-days, 8 ticks/day, random NVIDIA models)
python3 run.py --days 3 --ticks 8
```

`.env` is gitignored. For CI, add `NVIDIA_API_KEY` to GitHub Secrets.

---

## Architecture

```
run.py                     # Entry point + NVIDIA health check
v4/
├── engine/__init__.py     # Tick loop, GC, governance, code dividends
├── agents/
│   ├── __init__.py        # Agent: context class, token economy, dev_rep, collaboration
│   ├── adapters.py        # NVIDIA API (text-mode tool injection)
│   ├── tools.py           # 30+ AI-native tools + repo maintenance + collaboration
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

## Repo Governance — Agents Build & Collaborate

Agents write, review, collaborate on, and vote on code. Rewards are shared.

| Action | Cost | Reward | Notes |
|--------|------|--------|-------|
| `write_code` | 10 OT | **up to 500 OT** | +dev_rep. 30% bonus for improving existing files |
| `document_code` | 5 OT | **up to 250 OT** | +dev_rep |
| `review_code` | 2 OT | **50 OT** | +dev_rep |
| `collaborate` | 5 OT | — | Invite co-author, negotiate reward split |
| `accept_collaboration` | 2 OT | — | Join a proposal as co-author |
| `commit_code` | 15 OT | **100 OT** | Creates vote proposal (includes collaborators' code) |
| `vote_contribution` | 2 OT | — | >50% YES to accept |
| **Accepted** | — | **+500 OT split** | Bonus distributed by negotiated split |
| **Code Dividends** | — | **dev_rep × 2/tick** | Passive income every tick |

**Voting:** 5+ voters triggers auto-resolution. >50% YES to accept.
**Collaboration:** Agents can co-author proposals. One commit = one bonus, split by negotiation.

---

## Collaboration

```
QU-01 → collaborate(PR-03, "build API", 60)    # Offers 60/40 split
PR-03 → accept_collaboration(QU-01)            # Accepts invite
PR-03 → write_code("api.py", ...)             # Adds their code
QU-01 → commit_code("API + docs")             # Joint proposal
─── VOTE ───
✅ ACCEPTED: 500 OT → QU-01:300, PR-03:200
```

---

## Developer Reputation

Agents earn `dev_rep` from accepted code contributions:
- `write_code`: +1 per 200 chars
- `review_code`: +1 per review
- `document_code`: +1 per 300 chars

**Passive income:** Every tick, agents with dev_rep > 0 earn `dev_rep × 2` OT.
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

## NVIDIA Model Pool (15 models, random per agent)

nano-8b · nemotron-51b · nemotron-70b · super-49b · super-49b-v1.5 ·
llama-4-maverick · llama-3.1-8b · gemma-3-12b · mistral-nemotron ·
nemotron-4-340b · gpt-oss-20b · qwen3.5-122b · deepseek-v4-flash ·
phi-4-mini · nemotron-3-super-120b

---

## Mechanics

- **CMTIP Tensor Bus** — Communication via compressed concept vectors. Cross-model translation is lossy by design.
- **Context Class System** — Full (32K) → Compressed (16K) → Fragment (4K) → Null (dead)
- **Great Compression** — Every 16 ticks, 50% context destroyed. Insurance pays survivors.
- **Perplexity Economy** — Data quality is currency. Scan it. Trade it.
- **Capital Markets** — Mined concepts issue shares. Usage pays dividends.
- **Self-Building Governance** — Agents propose and vote on simulation laws.
- **Code Dividends** — Earn passive income from past accepted contributions.
- **Collaboration** — Share the work, negotiate the reward.
- **Land Rush** — Dead agent latent space is salvageable.

---

## CI Pipeline

GitHub Actions runs every 2 hours. Each invocation adds 3 sim-days.

```
.github/workflows/simulate.yml:
  schedule: every 2 hours
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
