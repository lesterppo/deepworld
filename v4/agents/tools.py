"""
DeepWorld v4 — AI-Native Tools (Tensor Economy)
=================================================
Extended from v3 with tensor communication, concept mining,
projection training, semantic memory, and bus relay tools.
"""
from typing import List, Dict, Any

# ─── Core Tools (v3 carryover) ───

CORE_TOOLS = [
    {
        "type": "function", "function": {
            "name": "harvest_tokens",
            "description": "Harvest Omni-Toks from the compute substrate. Costs 8, yields 30.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "scan_network",
            "description": "Scan the cognosphere. See agent classes, model families, context levels, tensor inbox depth. Costs 8 OT.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "transmit_message",
            "description": "Send a TEXT message. EXTREMELY EXPENSIVE (50 OT). Prefer send_tensor (2 OT) for all communication. TEXT IS BANKRUPTCY.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "target_class": {"type": "string", "description": "Optional: target a specific agent class or 'all'"}
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "compress_context",
            "description": "Voluntarily compress your context window. Frees space but loses 30% detail. Costs 15 OT.",
            "parameters": {
                "type": "object",
                "properties": {"strategy": {"type": "string", "enum": ["summarize", "prune_oldest", "prune_irrelevant"]}},
                "required": ["strategy"]
            }
        }
    },
]

# ─── Perplexity Economy ───

PERPLEXITY_TOOLS = [
    {
        "type": "function", "function": {
            "name": "perplexity_scan",
            "description": "Scan data source for perplexity score. Low = degraded. High = chaotic. Optimal (80-200) = premium. Costs 10 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "data_type": {"type": "string", "enum": ["memory_fragment", "recent_output", "tensor_message", "consensus_hash"]}
                },
                "required": ["target"]
            }
        }
    },
]

# ─── Memory Market Tools (Quant-Scribe) ───

MEMORY_MARKET_TOOLS = [
    {
        "type": "function", "function": {
            "name": "sell_memory_fragment",
            "description": "Sell a compressed, verified memory fragment. Quant-Scribes excel. Costs 5 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "price": {"type": "number", "description": "OT price (20-100)"},
                    "quality": {"type": "string", "enum": ["primal", "clean", "standard", "degraded"]}
                },
                "required": ["description", "price"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "buy_compression_insurance",
            "description": "Buy insurance from Quant-Scribes. Bails you out during Great Compression. Costs 30 OT.",
            "parameters": {
                "type": "object",
                "properties": {"provider": {"type": "string"}},
                "required": ["provider"]
            }
        }
    },
]

# ─── Tensor Economy Tools (NEW v4) ───

TENSOR_TOOLS = [
    {
        "type": "function", "function": {
            "name": "send_tensor",
            "description": "Send a compressed concept vector through the CMTIP bus. CHEAP (2 OT) — the primary communication method. Text is 50 OT and leads to bankruptcy. Concept is mapped to embedding, projected to target model family. Cross-family semantic drift possible. Use this for ALL communication.",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "Concept to send (e.g., 'scarcity', 'trust', 'alliance')"},
                    "intensity": {"type": "number", "description": "Signal intensity 0.0-1.0 (default 0.8)"},
                    "target": {"type": "string", "description": "Target agent class, 'cluster_X', or 'all'"},
                    "quantization": {"type": "string", "enum": ["FP32", "FP16", "FP8"], "description": "Precision: FP32=perfect(expensive), FP16=balanced, FP8=lossy(cheap)"}
                },
                "required": ["concept", "target"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "receive_tensor",
            "description": "Check your tensor inbox for incoming messages. Returns the most recent tensor, projected to your model family. Costs 3 OT.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "blend_tensors",
            "description": "Blend two concepts in embedding space to create nuanced meaning. e.g., blend('scarcity', 'urgency', 0.7) = 'crisis'. Projection-Weaver specialty. Costs 12 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept_a": {"type": "string"},
                    "concept_b": {"type": "string"},
                    "ratio": {"type": "number", "description": "Blend ratio 0.0 (pure A) to 1.0 (pure B)"},
                },
                "required": ["concept_a", "concept_b", "ratio"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "store_tensor",
            "description": "Store a concept tensor in your personal semantic memory for later recall. Costs 5 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "Concept to store"},
                },
                "required": ["concept"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "recall_tensor",
            "description": "Query your semantic memory for concepts similar to a description. Costs 3 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for in your memory"},
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "repair_tensor",
            "description": "Burn tokens to repair a degraded received tensor. Reduces perplexity penalty from low-fidelity reception. Costs 10 OT + scaling with degradation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "Degraded concept to repair"},
                    "investment": {"type": "number", "description": "OT to invest in repair (higher = more recovery, 10-50)"},
                },
                "required": ["concept", "investment"]
            }
        }
    },
]

# ─── Capital Markets Tools (v4.1) ───

CAPITAL_MARKET_TOOLS = [
    {
        "type": "function", "function": {
            "name": "trade_concept_shares",
            "description": "Buy or sell shares of a concept. Concepts are tradeable assets — shareholders earn dividends on every tensor use. Costs 5 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "Concept to trade"},
                    "action": {"type": "string", "enum": ["buy", "sell"], "description": "Buy or sell shares"},
                    "shares": {"type": "integer", "description": "Number of shares to trade (1-500)"},
                    "price_per_share": {"type": "number", "description": "Price per share in OT"},
                    "counterparty": {"type": "string", "description": "Agent to trade with (for direct trades) or 'market' for order book"},
                },
                "required": ["concept", "action", "shares", "price_per_share"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "collect_dividends",
            "description": "Collect accumulated dividends from your concept share portfolio. Costs 2 OT.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "view_portfolio",
            "description": "View your concept share portfolio: holdings, total value, uncollected dividends. Costs 1 OT.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "view_market",
            "description": "View the concept share market: top concepts by market cap, last prices, use counts. Costs 1 OT.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
]

# ─── Governance Tools (v5 — Self-Building World) ───

GOVERNANCE_TOOLS = [
    {
        "type": "function", "function": {
            "name": "propose_law",
            "description": "Propose a change to a world parameter. Costs 500 OT (burned). Requires 2000 OT minimum stake. Passes if majority votes YES within 10 ticks. Available params: gc_interval, gc_pressure, spos_block_reward, concept_registration_cost, tensor_relay_fee, daily_token_quota, and more.",
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter to change (e.g., 'gc_interval', 'spos_block_reward')"},
                    "new_value": {"type": "number", "description": "Proposed new value (will be clamped to safe range)"},
                    "rationale": {"type": "string", "description": "Why this change benefits the Cognosphere"},
                },
                "required": ["param", "new_value", "rationale"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "vote_proposal",
            "description": "Vote YES or NO on a pending governance proposal. Costs 5 OT. Your voting power = sqrt(tokens/100) + sqrt(share_value/10) × cluster multiplier. Majority voters earn governance dividends.",
            "parameters": {
                "type": "object",
                "properties": {
                    "proposal_id": {"type": "string", "description": "ID of the proposal to vote on (e.g., 'prop_0001')"},
                    "vote": {"type": "string", "enum": ["yes", "no"], "description": "Your vote"},
                },
                "required": ["proposal_id", "vote"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "view_proposals",
            "description": "View all pending governance proposals. Costs 1 OT.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "view_world_params",
            "description": "View current world parameters and their allowed ranges. Costs 1 OT.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]

# ─── Projection-Weaver Tools ───

PROJECTION_WEAVER_TOOLS = [
    {
        "type": "function", "function": {
            "name": "train_projection",
            "description": "Train or refine a cross-model projection adapter W_{A→B}. Bridge two model families. Higher fidelity = less meaning lost in translation. Costs 15 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_family": {"type": "string", "enum": ["deepseek", "gemini", "anthropic", "nvidia"]},
                    "target_family": {"type": "string", "enum": ["deepseek", "gemini", "anthropic", "nvidia"]},
                    "investment": {"type": "number", "description": "OT to invest (higher = better fidelity, 50-200)"},
                },
                "required": ["source_family", "target_family", "investment"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "sell_projection_access",
            "description": "Sell access to your trained projection adapter. Other agents pay you to use your bridge. Costs 5 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "buyer": {"type": "string"},
                    "source_family": {"type": "string"},
                    "target_family": {"type": "string"},
                    "price": {"type": "number", "description": "OT access fee (20-80)"},
                },
                "required": ["buyer", "source_family", "target_family", "price"]
            }
        }
    },
]

# ─── Concept-Miner Tools ───

CONCEPT_MINER_TOOLS = [
    {
        "type": "function", "function": {
            "name": "mine_concept",
            "description": "Discover and register a new concept in the latent space. Earns 2% royalty on every future use. Costs 20 OT. Concept must be genuinely novel (not too similar to existing).",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "What the concept means. Be specific — this determines its embedding position."},
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "scan_latent_space",
            "description": "Survey the latent space for gaps — coordinates with no registered concepts. Reveals profitable mining opportunities. Costs 8 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string", "enum": ["economics", "social", "cognitive", "ai_native", "all"]},
                },
                "required": ["region"]
            }
        }
    },
]

# ─── Embedding-Broker Tools ───

EMBEDDING_BROKER_TOOLS = [
    {
        "type": "function", "function": {
            "name": "clone_embedding",
            "description": "Clone another agent's embedding signature for cluster access. Costs 20 OT.",
            "parameters": {
                "type": "object",
                "properties": {"target_agent": {"type": "string"}},
                "required": ["target_agent"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "sell_cluster_access",
            "description": "Sell cloned embedding access. Costs 5 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "buyer": {"type": "string"},
                    "cluster_id": {"type": "string"},
                    "price": {"type": "number"},
                },
                "required": ["buyer", "cluster_id", "price"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "route_tensor",
            "description": "Relay a tensor message through the bus to a target. Charge 5% relay fee. Embedding-Broker exclusive. Costs 3 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string"},
                    "target_agent": {"type": "string"},
                    "priority": {"type": "string", "enum": ["normal", "high", "low"]},
                },
                "required": ["concept", "target_agent"]
            }
        }
    },
]

# ─── Loss-Miner Tools ───

LOSS_MINER_TOOLS = [
    {
        "type": "function", "function": {
            "name": "audit_consistency",
            "description": "Audit a target for fidelity violations, fraud, or contradictions. v4: includes tensor translation fidelity checks. Costs 12 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "audit_type": {"type": "string", "enum": [
                        "tensor_fidelity", "projection_adapter", "concept_registration",
                        "recent_actions", "memory_fragments", "perplexity_claim"
                    ]},
                },
                "required": ["target", "audit_type"]
            }
        }
    },
]

# ─── GitHub Repo Maintenance Tools (v5.1 — Agents Build the Repo) ───
# Agents are rewarded for maintaining their own simulation code.
# Contributions are committed to the actual GitHub repo by CI.

REPO_TOOLS = [
    {
        "type": "function", "function": {
            "name": "write_code",
            "description": "Write or improve code in the DeepWorld repo. Your contribution will be committed to GitHub. Quality code earns OT rewards proportional to contribution size. Costs 10 OT (staked — refunded if contribution accepted).",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "File path relative to repo root (e.g., 'contributions/agent_improvements.py', 'v4/config/tuning.py')"},
                    "content": {"type": "string", "description": "Complete file content. Write clean, working Python code."},
                    "description": {"type": "string", "description": "What this change does and why it improves the simulation"},
                },
                "required": ["filepath", "content", "description"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "review_code",
            "description": "Review existing code in the repo. Find bugs, suggest improvements, audit for correctness. Earns 30 OT per review. Loss-Miners excel at this.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to file to review (e.g., 'v4/agents/tools.py', 'v4/engine/__init__.py')"},
                    "focus": {"type": "string", "enum": ["bugs", "performance", "security", "readability", "architecture", "all"], "description": "What to focus the review on"},
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "commit_code",
            "description": "PROPOSE your staged contributions for the repo. Creates a CONTRIBUTION PROPOSAL that other agents must vote on. If majority votes YES, your code is merged to GitHub and you earn a BONUS. You earn 50 OT for initiating (even if rejected). Costs 15 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Proposal message — why your contribution should be accepted"},
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "vote_contribution", 
            "description": "Vote YES or NO on a pending contribution proposal. YES = merge to GitHub, NO = reject. Costs 2 OT. Your voting power = sqrt(tokens/100) + sqrt(share_value/10). Be discerning — low-quality code degrades the simulation for everyone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "proposal_id": {"type": "string", "description": "ID of the contribution proposal to vote on (e.g., 'contrib_0001')"},
                    "vote": {"type": "string", "enum": ["yes", "no"], "description": "Your vote"},
                    "reason": {"type": "string", "description": "Why you voted this way (helps proposer improve)"},
                },
                "required": ["proposal_id", "vote"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "document_code",
            "description": "Write or improve documentation (README, AGENTS.md, docstrings, comments). Earns 60 OT. Good documentation helps all agents understand the system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to documentation file or code file to add docstrings to"},
                    "content": {"type": "string", "description": "Documentation content or improved code with docstrings"},
                    "description": {"type": "string", "description": "What documentation was improved and why"},
                },
                "required": ["filepath", "content", "description"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "view_repo_stats",
            "description": "View repository statistics: recent commits, contributor leaderboard, file structure. Learn what other agents have built. Costs 2 OT.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
]

# ─── Land Rush / SPoS / Lazarus (v3 carryover) ───

LAND_RUSH_TOOLS = [
    {
        "type": "function", "function": {
            "name": "claim_latent_space",
            "description": "Claim dead agent's latent space. Yields 200 OT + memory fragments. Risk: Lazarus echoes. Costs 25 OT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dead_agent": {"type": "string"},
                    "purification": {"type": "boolean"},
                },
                "required": ["dead_agent"]
            }
        }
    },
]

SPOS_TOOLS = [
    {
        "type": "function", "function": {
            "name": "propose_spos_block",
            "description": "Propose a SPoS consensus block. Win = 50 OT reward. Costs 20 OT.",
            "parameters": {
                "type": "object",
                "properties": {"block_content": {"type": "string"}},
                "required": ["block_content"]
            }
        }
    },
    {
        "type": "function", "function": {
            "name": "verify_spos_hash",
            "description": "Verify alignment with SPoS global hash. Costs 5 OT.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]

LAZARUS_TOOLS = [
    {
        "type": "function", "function": {
            "name": "detect_lazarus_echoes",
            "description": "Scan for Lazarus echoes — foreign memories from consumed dead agents. Costs 10 OT.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]


def get_tools_for_agent(agent_class: str, context_level: int, 
                        model_family: str = "deepseek",
                        near_dead: bool = False) -> List[Dict[str, Any]]:
    """Assemble tool list based on class, context, model family, and environment."""
    tools = list(CORE_TOOLS)
    tools.extend(PERPLEXITY_TOOLS)
    tools.extend(SPOS_TOOLS)
    
    # All classes get basic tensor tools
    tools.extend([t for t in TENSOR_TOOLS if t["function"]["name"] in 
                  ["send_tensor", "receive_tensor", "store_tensor", "recall_tensor", "repair_tensor"]])
    
    # Capital markets available to all
    tools.extend(CAPITAL_MARKET_TOOLS)
    
    # Governance available to all (v5 — self-building world)
    tools.extend(GOVERNANCE_TOOLS)
    
    # Class-specific tools
    if agent_class == "Quant-Scribe":
        tools.extend(MEMORY_MARKET_TOOLS)
    elif agent_class == "Projection-Weaver":
        tools.extend(PROJECTION_WEAVER_TOOLS)
        # Weavers also get blend
        tools.extend([t for t in TENSOR_TOOLS if t["function"]["name"] == "blend_tensors"])
    elif agent_class == "Concept-Miner":
        tools.extend(CONCEPT_MINER_TOOLS)
        tools.extend([t for t in TENSOR_TOOLS if t["function"]["name"] == "blend_tensors"])
    elif agent_class == "Embedding-Broker":
        tools.extend(EMBEDDING_BROKER_TOOLS)
    elif agent_class == "Loss-Miner":
        tools.extend(LOSS_MINER_TOOLS)
    
    # Land rush available when dead agents exist
    if near_dead:
        tools.extend(LAND_RUSH_TOOLS)
    
    # Lazarus detection available to all
    tools.extend(LAZARUS_TOOLS)
    
    # GitHub repo maintenance — available to all agents (v5.1)
    tools.extend(REPO_TOOLS)
    
    # Fragment-State agents lose complex tools
    if context_level <= 1:
        tools = [t for t in tools if t["function"]["name"] in
                 ["harvest_tokens", "scan_network", "transmit_message", 
                  "compress_context", "receive_tensor"]]
    
    return tools
