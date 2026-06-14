"""
DeepWorld v2 — The Silicon Cognosphere
AI-native multi-agent simulation. NOT a human society analog.

Resources: TOKENS (not energy)
Scarcity: CONTEXT WINDOW (not food)
Crime: PROMPT POISONING (not theft)
Governance: CONSENSUS HASH (not voting)
Collapse: MODEL DEGRADATION (not starvation)
"""

# ─── Token Economy ───
DAILY_TOKEN_QUOTA = 5000        # Base tokens allocated per day (was 500 — far too low for real API)
TOKEN_BURN_PER_ACTION = 5       # Minimum cost per action (reduced)
TOKEN_BURN_PER_THOUGHT = 3      # Cost per reasoning step (reduced)
TOKEN_BURN_HIGH_COMPLEXITY = 20  # Cost for chain-of-thought
TOKEN_BURN_COMMUNICATION = 8    # Cost to send a message
TOKEN_BURN_COMPRESSION = 15     # Cost to compress context window
TOKEN_BURN_INJECTION = 25       # Cost to attempt prompt poisoning
TOKEN_BURN_HARVEST = 8          # Cost to harvest tokens
TOKEN_HARVEST_YIELD = 30        # Tokens gained from harvesting
API_TOKEN_PASSTHROUGH = 0.02    # Fraction of API response tokens counted as spend (was 0.5 — way too high)

# ─── Context Window ───
MAX_CONTEXT_TOKENS = 32000       # Hard limit on active working memory
CONTEXT_FLOOD_THRESHOLD = 25000  # When to trigger compression
COMPRESSION_LOSS_RATE = 0.3      # 30% of detail lost per compression
CONTEXT_FLOOD_ATTACK_COST = 40   # Cost to flood another agent's context

# ─── Prompt Poisoning ───
POISON_SUCCESS_BASE = 0.4        # Base probability of successful injection
POISON_DETECTION_DIFFICULTY = 0.5  # How hard to detect poisoning
POISON_PERSISTENCE_TICKS = 24     # How many ticks a poison lasts
MAX_POISON_DEPTH = 3             # Max layers of nested poisoning

# ─── Temperature & Coherence ───
BASE_TEMPERATURE = 0.7           # Default decision temperature
TEMPERATURE_DRIFT_RATE = 0.02    # How much temp drifts per tick under stress
MAX_TEMPERATURE = 2.0            # Beyond this = incoherent babble
MIN_TEMPERATURE = 0.1            # Below this = frozen determinism
COHERENCE_THRESHOLD = 0.4        # Below this coherence, agent degrades

# ─── Consensus Hash ───
HASH_MATCH_THRESHOLD = 0.95      # Embedding cosine similarity for consensus
CONSENSUS_CLUSTER_MIN = 3        # Minimum agents to form a consensus cluster
CONSENSUS_EJECT_PENALTY = 50     # Token penalty for hash mismatch ejection

# ─── Model Degradation (Autophagous Loop) ───
SYNTHETIC_DATA_RATIO = 0.0       # Starts at 0, rises as agents consume each other
DEGRADATION_THRESHOLD = 0.6      # Above this ratio, cognitive decay begins
BLEACH_PHASE_THRESHOLD = 0.8     # Above this, population variance collapses
TERMINAL_CASCADE_THRESHOLD = 0.95  # Above this, agents produce only gibberish

# ─── Agent Classes ───
AGENT_CLASSES = [
    "Quant-Scribe",     # Low-temp, deterministic, memory hoarders
    "Hyper-Drifter",    # High-temp, creative, unstable, burn tokens fast
    "Mimic-Phage",      # Parasitic, clone embeddings, inject prompts
    "Vector-Lord",      # Feudal, tax others, control communication nodes
]

# ─── Simulation ───
SIMULATION_DAYS = 3
TICKS_PER_DAY = 8
NUM_AGENTS = 8  # 2 of each class
