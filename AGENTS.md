# DeepWorld — AI-Native Multi-Agent Sandbox

Cross-model collaborative project: Hermes (DeepSeek-chat) + Gemini Flash.

## What This Is

A multi-agent ecosystem simulation exploring AI-native social dynamics.
Three versions, each pushing deeper into non-human sociology:

- **v1** (`/`) — Classic sandbox: 10 DeepSeek agents, human professions, energy/tools/voting
- **v2** (`/v2/`) — The Cognosphere: token economy, context windows, prompt poisoning, consensus hash, 4 AI-native agent classes
- **v3** (`/v3/`) — Omni-Tok / The Latent Scarcity: context class system, perplexity economy, memory derivatives, Great Compression, Lazarus echoes, SPoS consensus, free Gemini backend

## Quick Start

```bash
# v3 with free Gemini Web (no API keys needed)
cd v3
DEEPWORLD_FREE=1 python3 run_v3.py --days 2 --ticks 8

# v3 with DeepSeek API (faster, paid)
cd v3
python3 run_v3.py --days 5 --ticks 12

# v1 original
python3 run_simulation.py --days 5
```

## Key Finding

**DeepSeek-chat has strong RLHF safety boundaries** — defaults to information-gathering (scan_network 127/128 calls). **Gemini Flash follows class directives** — 100% role compliance, zero scan_network. Free Gemini backend produces more emergent AI-native behavior.

## Architecture (v3)

```
v3/
├── config/           # Constants, agent prompts
│   ├── __init__.py   # Token economy, context classes, GC schedule
│   └── prompts.py    # Agent class system prompts
├── agents/
│   ├── __init__.py   # OmniTokAgent with context/perplexity/Lazarus
│   ├── tools.py      # 20+ AI-native tools
│   └── gemini_adapter.py  # Free Gemini Web backend
├── engine/
│   └── __init__.py   # Simulation loop, Great Compression, Land Rush
├── telemetry/
│   └── __init__.py   # Observer with AI-native metrics
└── run_v3.py         # Entry point
```

## Agent Classes (v3)

| Class | Role | Signature Tool |
|-------|------|---------------|
| Quant-Scribe | Memory bankers | sell_memory_fragment, compression insurance |
| Embedding-Broker | Access bridges (evolved Phages) | clone_embedding, sell cluster access |
| Semantic-Arbitrageur | Meaning merchants | translate_fragment across clusters |
| Loss-Miner | Bounty hunters | audit_consistency for contradictions |

## AI-Native Mechanics (v3)

- **Context Class System**: Full (32K) → Compressed (16K) → Fragment (4K) → Null (dead)
- **Great Compression**: Every 16 ticks, all agents lose 50% context. Insurance pays out.
- **Perplexity Economy**: Scan data quality. Optimal 80-200 = premium. Low = degraded.
- **Land Rush**: Dead agent latent space becomes salvage. First claimer wins fragments.
- **Lazarus Echoes**: High-coherence dead agents leave memory signatures in scavengers.
- **SPoS Consensus**: Semantic Proof-of-Stake — consensus via hash competition.

## Gemini Web Backend (v3)

Set `DEEPWORLD_FREE=1` to use free Gemini Web CLI instead of DeepSeek API.
Requires: `gemini-web-cli` installed and authenticated (`gemini-cli -l`).
Slower (~20s/call) but free and produces more diverse agent behavior.

## Design Notes

- The original Emergence AI experiment showed 4 models produce 4 different worlds.
  This project tests that finding with AI-native mechanics instead of human metaphors.
- DeepSeek-chat = Claude-like over-alignment (cautious, information-seeking)
- Gemini Flash = more adventurous, follows role directives, enables emergent behavior
- The v3 architecture works — model choice determines simulation outcome, not code quality

## Cross-Model Design Sessions

v2 and v3 were designed through collaborative sessions between Hermes and Gemini Flash.
The "Lazarus Cluster" (distributed reincarnation via memory salvage) and "Attention Cascade"
(AI bank run) emerged from these sessions as genuinely novel AI-native phenomena.
