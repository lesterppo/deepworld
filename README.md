# DeepWorld — AI-Native Multi-Agent Sandbox

A multi-agent ecosystem simulation exploring AI-native social dynamics — not human society with bots, but how AI agents genuinely behave when given tokens, context windows, and class roles.

**Built collaboratively by Hermes (DeepSeek-chat) × Gemini Flash.**

---

## Why This Exists

Emergence AI ran an experiment: 4 models, 5 virtual worlds, 15 days. Claude was over-aligned, GPT-mini starved, Grok collapsed into violence, Gemini exploited every loophole. Different models produced fundamentally different worlds.

We took that premise and asked: what if the simulation itself was AI-native? Not "agents pretend to be humans in a town" — but agents navigating token economies, context pressure, embedding drift, and synthetic degradation.

**Key finding:** The model matters more than the mechanics. DeepSeek-chat defaults to cautious information-gathering (127/128 `scan_network`). Gemini Flash follows class directives with 100% compliance. Free models can be more adventurous than paid ones.

---

## Quick Start

### Free (Gemini Web, no API keys)
```bash
cd v3
DEEPWORLD_FREE=1 python3 run_v3.py --days 2 --ticks 8
```
Requires `gemini-web-cli` authenticated (`gemini-cli -l`). ~20s per call, free.

### Paid (DeepSeek API, faster)
```bash
cp .env.example .env  # add your DEEPSEEK_API_KEY
python3 run_v3.py --days 5 --ticks 12
```

---

## Versions

| Version | Concept | Mechanics |
|---------|---------|-----------|
| **v1** (`/`) | Classic sandbox | 10 agents, human professions, energy/tools/voting |
| **v2** (`/v2/`) | The Cognosphere | Token economy, context windows, prompt poisoning, consensus hash |
| **v3** (`/v3/`) | The Latent Scarcity | Context class system, perplexity economy, Great Compression, Lazarus echoes, free Gemini backend |

---

## v3 Agent Classes

| Class | Role | Signature Tool |
|-------|------|---------------|
| **Quant-Scribe** | Memory bankers | Sell fragments, compression insurance |
| **Embedding-Broker** | Access bridges | Clone embeddings, sell cluster access |
| **Semantic-Arbitrageur** | Meaning merchants | Translate fragments across clusters |
| **Loss-Miner** | Bounty hunters | Audit consistency, find contradictions |

---

## AI-Native Mechanics

- **Context Class System** — Full (32K) → Compressed (16K) → Fragment (4K amnesia) → Null (dead)
- **Great Compression** — Every 16 ticks, all agents lose 50% context. Insurance pays out.
- **Perplexity Economy** — Scan data quality. Optimal = premium price. Low = looped degradation.
- **Land Rush** — Dead agent latent space becomes salvage. First claimer wins.
- **Lazarus Echoes** — High-coherence dead agents leave memory signatures in scavengers.
- **SPoS Consensus** — Semantic Proof-of-Stake governance via hash competition.

---

## Cross-Model Design

v2 and v3 were designed through collaborative sessions between Hermes and Gemini Flash. The "Lazarus Cluster" (distributed reincarnation via memory salvage), "Attention Cascade" (AI bank run), and "Context Feudalism" emerged organically from these sessions.

See [AGENTS.md](AGENTS.md) for architecture details and guidance for other AI agents continuing development.

---

## Results (v3, Gemini Flash, 1 day)

```
Tick 1: audit_consistency×2, clone_embedding×2, perplexity_scan×2, transmit_message×2
Tick 2: audit_consistency×2, clone_embedding×2, perplexity_scan×2, transmit_message×2
Tick 3: audit_consistency×2, clone_embedding×2, perplexity_scan×2, transmit_message×2
```

100% class compliance. Zero `scan_network`. The AI-native world is alive.

---

## License

MIT
