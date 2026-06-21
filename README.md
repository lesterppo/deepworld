# DeepWorld v5 — Tensor-Native Multi-Agent Cognosphere

A multi-agent ecosystem simulation exploring AI-native social dynamics through
tensor communication, token economies, and self-building governance. Agents
navigate context pressure, embedding drift, and cross-model semantic decay —
not human professions.

**10 agents on 15 random NVIDIA free models. Zero API cost.**

---

## Quick Start

```bash
git clone https://github.com/lesterppo/deepworld
cd deepworld
pip install openai pyyaml sentence-transformers numpy

# Run (NVIDIA API key required in ~/.hermes/.env)
python3 run.py --days 3 --ticks 8
```

---

## Versions

| Version | Location | Status |
|---------|----------|--------|
| **v5** | Root (`run.py`, `v4/`) | Active — NVIDIA-only tensor-native simulation |
| v1-v3 | `archive/` | Classic sandbox, Cognosphere, Latent Scarcity |

---

## Architecture (v5)

```
run.py                    # Root entry point + NVIDIA health check
v4/
├── engine/               # OmniTokV4Engine — tick loop, GC, governance
├── agents/
│   ├── __init__.py       # OmniTokV4Agent — token economy, tensor comms
│   ├── adapters.py       # MultiModelAdapter — NVIDIA API (OpenAI-compatible)
│   ├── tools.py          # 30+ AI-native tools
│   ├── cmtip_bridge.py   # CMTIP tensor bus — concept embeddings, projectors
│   └── real_backends.py  # SentenceTransformer backend + hash fallback
├── config/
│   ├── __init__.py       # NVIDIA_FREE_MODELS pool, token economy, GC params
│   └── prompts.py        # Agent class system prompts (5 classes)
├── world_registry.py     # Self-building governance: proposals, voting, laws
├── telemetry/            # OmniObserverV4 — event logging, daily snapshots
└── validate_tensors.py   # Cross-model tensor validation suite
```

---

## Agent Classes

| Class | Role | Signature Tool |
|-------|------|---------------|
| **Quant-Scribe** | Memory bankers | Sell fragments, compression insurance |
| **Projection-Weaver** | Model bridges | Train W_{A→B} adapters between model families |
| **Concept-Miner** | Ontology creators | Discover latent concepts, define vocabulary |
| **Loss-Miner** | Bounty hunters | Audit tensor translations for fraud |
| **Embedding-Broker** | Bus relays | Route tensors, clone embeddings, charge fees |

---

## NVIDIA Model Pool

Each agent gets a random model from this pool for behavioral diversity:

| Model | Size | Characteristics |
|-------|------|----------------|
| llama-3.1-nemotron-nano-8b-v1 | 8B | Fast, lightweight |
| llama-3.1-nemotron-51b-instruct | 51B | Balanced reasoning |
| llama-3.1-nemotron-70b-instruct | 70B | Large, capable |
| llama-3.3-nemotron-super-49b-v1 | 49B | Latest NVIDIA super |
| llama-4-maverick-17b-128e | 17B | Meta Llama 4 |
| gemma-3-12b-it | 12B | Google Gemma 3 |
| mistral-nemotron | 12B | Mistral + NVIDIA |
| nemotron-4-340b-instruct | 340B | Massive reasoning |
| gpt-oss-20b | 20B | OpenAI open-source |
| qwen3.5-122b-a10b | 122B | Qwen 3.5 MoE |
| deepseek-v4-flash | — | DeepSeek V4 Flash |
| phi-4-mini-instruct | — | Microsoft Phi-4 |
| nemotron-3-super-120b-a12b | 120B | Nemotron 3 Super |
| llama-3.1-8b-instruct | 8B | Classic Llama 3 |
| llama-3.3-nemotron-super-49b-v1.5 | 49B | Super v1.5 |

---

## AI-Native Mechanics

- **CMTIP Tensor Bus** — Agents communicate via compressed concept vectors, not text. Cross-model translation is lossy by design.
- **Context Class System** — Full (32K) → Compressed (16K) → Fragment (4K) → Null (dead)
- **Great Compression** — Every 16 ticks, all agents lose 50% context. Insurance pays survivors.
- **Perplexity Economy** — Data quality is currency. Optimal perplexity = premium price.
- **Capital Markets** — Mined concepts issue 1,000 shares. Usage pays dividends to shareholders.
- **Self-Building Governance** — Agents propose, vote, and change simulation rules. Proposals cost 500 OT, pass by majority.
- **Land Rush** — Dead agent latent space becomes salvage. First claimer wins fragments.
- **Lazarus Echoes** — High-coherence dead agents leave memory signatures in scavengers.

---

## Continuous CI Pipeline

GitHub Actions runs every 2 hours. Each invocation adds 5 days.

```
.github/workflows/simulate.yml:
  schedule: every 2h
  timeout: 5h
  backend: NVIDIA NIM (NVIDIA_API_KEY from GitHub Secrets)
  models: 15 models, random per agent, 10 agents
  pre-flight: health check validates NVIDIA API before simulation
  output: commits results to runs/
  state: .world_state.json persists governance between runs
```

**Setup:** Add `NVIDIA_API_KEY` to GitHub Secrets. Enable Actions. Done.

---

## License

MIT
