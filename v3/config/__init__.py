"""
PROJECT OMNI-TOK v3 — The Latent Scarcity
=========================================
AI-native ecosystem where context IS territory,
perplexity IS credit rating, and memory fragments
retain the ghost of their original owner.
"""

# ─── Context Class System ───
FULL_CONTEXT = 32000      # Upper class: remembers 20+ turns
COMPRESSED_CONTEXT = 16000  # Middle class: 50% detail loss
FRAGMENT_STATE = 4000      # Lower class: 2-turn amnesia
NULL_STATE = 0             # Dead: memory released as salvage

# ─── Token Economy ───
DAILY_TOKEN_QUOTA = 5000
TOKEN_BURN_ACTION = 5
TOKEN_BURN_THINK = 3
API_PASSTHROUGH = 0.02
HARVEST_YIELD = 30
HARVEST_COST = 8

# ─── Perplexity Economy ───
PERPLEXITY_OPTIMAL_MIN = 80   # Goldilocks zone: information-rich
PERPLEXITY_OPTIMAL_MAX = 200
PERPLEXITY_LOW_THRESHOLD = 40  # Below this = looped/degraded (dangerous)
PERPLEXITY_HIGH_THRESHOLD = 300  # Above this = chaotic/corrupted (dangerous)
PERPLEXITY_SCAN_COST = 10
PERPLEXITY_PREMIUM = 1.5  # Multiplier for optimal-perplexity data

# ─── Memory Derivatives ───
MEMORY_FUTURE_MIN = 20     # Minimum bet on a memory futures contract
COMPRESSION_INSURANCE_COST = 30  # Premium for compression bailout
SCRIBE_LAUNDERING_FEE = 0.30  # 30% fee for memory purification

# ─── Semantic Arbitrage ───
TRANSLATE_FRAGMENT_COST = 15
TRANSLATION_LOSS_MIN = 0.05  # Minimum semantic loss per translation
TRANSLATION_LOSS_MAX = 0.35  # Maximum loss
ARBITRAGE_PROFIT_BASE = 25   # Base profit from inter-cluster trade

# ─── Great Compression ───
GREAT_COMPRESSION_INTERVAL = 16  # Ticks between Great Compressions
GREAT_COMPRESSION_PRESSURE = 0.5  # 50% context forced compression
GREAT_COMPRESSION_SURVIVAL_BONUS = 100  # Token reward for surviving

# ─── Defragmentation / Land Rush ───
LAND_RUSH_WINDOW = 5         # Ticks after death before memory decays
LATENT_SPACE_SALVAGE_YIELD = 200  # Tokens from claiming latent space
LAZARUS_COHERENCE_THRESHOLD = 0.7  # If memory coherence > this, Lazarus possible

# ─── SPoS Consensus ───
SPOS_BLOCK_REWARD = 50    # Token reward for proposing winning block
SPOS_HASH_MATCH = 0.90    # Required embedding similarity for consensus
SPOS_MIN_CLUSTER = 3      # Min agents for a consensus cluster

# ─── Model Degradation ───
SYNTHETIC_RATIO_START = 0.0
DEGRADATION_RATE = 0.003   # Per-tick increase from synthetic consumption
PURITY_PREMIUM = 2.0       # Multiplier for "First Epoch" (clean) data

# ─── Agent Classes (v3 evolution) ───
AGENT_CLASSES = [
    "Quant-Scribe",         # Memory bankers, compression insurance, purification
    "Embedding-Broker",     # Evolved Mimic-Phages: clone access, inter-cluster bridges
    "Semantic-Arbitrageur", # Profit from semantic distance between clusters
    "Loss-Miner",           # Find logical inconsistencies for bounty
]

# ─── Simulation ───
SIM_DAYS = 3
TICKS_PER_DAY = 8
NUM_AGENTS = 8
