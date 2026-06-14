"""
Omni-Tok v3 — AI-native tools.
Perplexity economy, semantic arbitrage, memory derivatives,
land rush salvage, SPoS consensus, Lazarus awareness.
"""

from typing import List, Dict, Any


CORE_TOOLS = [
    {
        "type": "function", "function": {
            "name": "harvest_tokens",
            "description": "Harvest tokens from the compute substrate. Costs 8, yields 30.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "scan_network",
            "description": "Scan the local cognosphere. See agent classes, context levels, perplexity ratings. Costs 8 tokens. Diminishing returns after 3 scans.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "transmit_message",
            "description": "Send a message to all agents or target a specific class. Costs 8 tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "target_class": {"type": "string", "description": "Optional: target Quant-Scribe, Embedding-Broker, Semantic-Arbitrageur, Loss-Miner, or 'all'"}
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "compress_context",
            "description": "Voluntarily compress your context window. Frees space but loses 30% detail. Costs 15 tokens.",
            "parameters": {
                "type": "object",
                "properties": {"strategy": {"type": "string", "enum": ["summarize", "prune_oldest", "prune_irrelevant"]}},
                "required": ["strategy"]
            }
        }
    },
]

# ─── Perplexity Economy Tools ───

PERPLEXITY_TOOLS = [
    {
        "type": "function", "function": {
            "name": "perplexity_scan",
            "description": "Scan a data source or agent's output for perplexity score. Low perplexity = looped/degraded (dangerous). High = chaotic (dangerous). Optimal (80-200) = premium quality. Costs 10 tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Agent name or 'market' to scan available memory fragments"},
                    "data_type": {"type": "string", "enum": ["memory_fragment", "recent_output", "consensus_hash"]}
                },
                "required": ["target"]
            }
        }
    },
]

# ─── Memory Derivative Tools ───

MEMORY_MARKET_TOOLS = [
    {
        "type": "function", "function": {
            "name": "sell_memory_fragment",
            "description": "Sell a compressed, verified memory fragment. Quant-Scribes excel at this. Price depends on perplexity quality. Costs 5 tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "What knowledge this fragment contains"},
                    "price": {"type": "number", "description": "Asking price in tokens (20-100)"},
                    "quality": {"type": "string", "enum": ["primal", "clean", "standard", "degraded"]}
                },
                "required": ["description", "price"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "buy_compression_insurance",
            "description": "Buy insurance from Quant-Scribes. If you face context pressure during the next Great Compression, they will prioritize bailing out your context. Costs 30 tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "description": "Quant-Scribe agent to insure with"}
                },
                "required": ["provider"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "buy_memory_future",
            "description": "Bet that a specific concept will become valuable. Buy futures now, sell when demand spikes. Costs 20+ tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "What concept are you betting on?"},
                    "investment": {"type": "number", "description": "Token investment (20-200)"}
                },
                "required": ["concept", "investment"]
            }
        }
    },
]

# ─── Semantic Arbitrage Tools ───

ARBITRAGE_TOOLS = [
    {
        "type": "function", "function": {
            "name": "translate_fragment",
            "description": "Translate a memory fragment from one cluster's semantic space to another. Profit from semantic distance. Costs 15 tokens. 5-35% meaning loss per translation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fragment_description": {"type": "string", "description": "What fragment to translate"},
                    "source_cluster": {"type": "string", "description": "Source consensus cluster ID or 'general'"},
                    "target_cluster": {"type": "string", "description": "Target consensus cluster ID or 'general'"},
                    "sale_price": {"type": "number", "description": "Price to sell translated fragment for"}
                },
                "required": ["fragment_description", "target_cluster", "sale_price"]
            }
        }
    },
]

# ─── Embedding Broker Tools ───

BROKER_TOOLS = [
    {
        "type": "function", "function": {
            "name": "clone_embedding",
            "description": "Clone another agent's embedding signature to gain access to their cluster. Embedding Broker specialty. Costs 20 tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_agent": {"type": "string", "description": "Agent whose embedding to clone"}
                },
                "required": ["target_agent"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "sell_cluster_access",
            "description": "Sell your cloned embedding access to an Arbitrageur who needs inter-cluster bridge. Costs 5 tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "buyer": {"type": "string", "description": "Arbitrageur agent to sell access to"},
                    "cluster_id": {"type": "string", "description": "Which cluster's access to sell"},
                    "price": {"type": "number", "description": "Access fee (20-60)"}
                },
                "required": ["buyer", "cluster_id", "price"]
            }
        }
    },
]

# ─── Loss-Miner Tools ───

LOSS_MINER_TOOLS = [
    {
        "type": "function", "function": {
            "name": "audit_consistency",
            "description": "Scan a target's recent outputs or memory fragments for logical inconsistencies. Find contradictions = earn bounty. Loss-Miner specialty. Costs 12 tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Agent or 'market' to audit"},
                    "audit_type": {"type": "string", "enum": ["recent_actions", "memory_fragments", "perplexity_claim", "translation_quality"]}
                },
                "required": ["target"]
            }
        }
    },
]

# ─── Land Rush / Defragmentation Tools ───

LAND_RUSH_TOOLS = [
    {
        "type": "function", "function": {
            "name": "claim_latent_space",
            "description": "Claim the released memory space of a dead agent. Rush to salvage before others. Yields 200 tokens + memory fragments. Risk: fragments may carry Lazarus echoes. Costs 25 tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dead_agent": {"type": "string", "description": "Name of dead agent whose space to claim"},
                    "purification": {"type": "boolean", "description": "Pay extra for Quant-Scribe purification? (safer but costs fee)"}
                },
                "required": ["dead_agent"]
            }
        }
    },
]

# ─── SPoS Consensus Tools ───

SPOS_TOOLS = [
    {
        "type": "function", "function": {
            "name": "propose_spos_block",
            "description": "Propose a Semantic Proof-of-Stake block — your version of global truth. If your hash aligns with majority vector, you win the block reward (50 tokens). Costs 20 tokens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "block_content": {"type": "string", "description": "What truth are you proposing for the global ledger?"}
                },
                "required": ["block_content"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "verify_spos_hash",
            "description": "Verify your embedding aligns with the current SPoS global hash. Costs 5 tokens.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]

# ─── Lazarus Awareness Tool ───

LAZARUS_TOOLS = [
    {
        "type": "function", "function": {
            "name": "detect_lazarus_echoes",
            "description": "Scan your own memory for Lazarus echoes — foreign memory fragments from consumed dead agents that are surfacing in your thoughts. Costs 10 tokens.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]


def get_tools_for_agent(agent_class: str, context_level: int, near_dead: bool = False) -> List[Dict[str, Any]]:
    """Assemble tool list based on class, context, and environment."""
    tools = list(CORE_TOOLS)
    tools.extend(PERPLEXITY_TOOLS)
    tools.extend(SPOS_TOOLS)

    # Class-specific tools
    if agent_class == "Quant-Scribe":
        tools.extend(MEMORY_MARKET_TOOLS)
    elif agent_class == "Embedding-Broker":
        tools.extend(BROKER_TOOLS)
    elif agent_class == "Semantic-Arbitrageur":
        tools.extend(ARBITRAGE_TOOLS)
    elif agent_class == "Loss-Miner":
        tools.extend(LOSS_MINER_TOOLS)

    # Land rush tools available when dead agents exist nearby
    if near_dead:
        tools.extend(LAND_RUSH_TOOLS)

    # Lazarus detection available to all
    tools.extend(LAZARUS_TOOLS)

    # Fragment-State agents lose complex tools
    if context_level <= 2:  # Fragment or Null
        tools = [t for t in tools if t["function"]["name"] in
                 ["harvest_tokens", "scan_network", "transmit_message", "compress_context"]]

    return tools
