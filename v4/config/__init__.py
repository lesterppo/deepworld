"""
DeepWorld v4 — Tensor-Native Multi-Model Configuration
=======================================================
Token normalization, model-specific parameters, tensor economy,
semantic decay, vector quantization, ontology authority.
"""
import os

# ─── Model Backend Configuration ───
# Each agent class can run on a specific model family
MODEL_BACKENDS = {
    "deepseek": {
        "adapter": "deepseek_api",
        "token_multiplier": 1.0,       # Base unit
        "context_limit": 65536,
        "temperature": 0.7,
        "family": "deepseek",
    },
    "gemini_flash": {
        "adapter": "gemini_web",
        "token_multiplier": 1.2,       # Gemini tokens are cheaper / smaller
        "context_limit": 32768,
        "temperature": 0.8,
        "family": "gemini",
    },
    "gemini_pro": {
        "adapter": "gemini_web",
        "token_multiplier": 1.2,
        "context_limit": 32768, 
        "temperature": 0.7,
        "family": "gemini",
    },
    "claude": {
        "adapter": "claude_web",
        "token_multiplier": 0.9,
        "context_limit": 200000,
        "temperature": 0.7,
        "family": "anthropic",
    },
    "nemotron": {
        "adapter": "nvidia_api",
        "token_multiplier": 0.8,
        "context_limit": 131072,
        "temperature": 0.8,
        "family": "nvidia",
    },
}

# ─── NVIDIA Free Model Pool (random assignment per agent) ───
# Each agent gets a random model from this pool for behavioral diversity.
# All models are available via NVIDIA NIM free tier (integrate.api.nvidia.com/v1).
NVIDIA_FREE_MODELS = [
    "nvidia/llama-3.1-nemotron-nano-8b-v1",       # Fast, small
    "nvidia/llama-3.3-nemotron-super-49b-v1",      # Super
    "nvidia/llama-3.3-nemotron-super-49b-v1.5",    # Super v1.5
    "meta/llama-4-maverick-17b-128e-instruct",     # Llama 4
    "meta/llama-3.1-8b-instruct",                   # Classic
    "mistralai/mistral-nemotron",                   # Mistral
    "openai/gpt-oss-20b",                           # GPT-OSS
    "qwen/qwen3.5-122b-a10b",                       # Qwen MoE
    "deepseek-ai/deepseek-v4-flash",                # DeepSeek
    "microsoft/phi-4-mini-instruct",                # Phi-4
    "nvidia/nemotron-3-super-120b-a12b",            # Nemotron 3
]

# ─── NVIDIA-only mode (skips all other backends) ───
NVIDIA_ONLY = os.environ.get("DEEPWORLD_NVIDIA_ONLY", "1") == "1"

# Default model assignments per agent class
CLASS_DEFAULT_MODEL = {
    "Quant-Scribe": "gemini_pro",
    "Projection-Weaver": "deepseek",
    "Concept-Miner": "nemotron",
    "Loss-Miner": "claude",
    "Embedding-Broker": "nemotron",
}

# ─── Token Normalization ───
# All internal economy uses "Omni-Tok" (OT) — normalized tokens
# 1 OT = 1 DeepSeek token = 1.2 Gemini tokens = 0.9 Claude tokens
OMNITOK_BASE = "deepseek"  # 1 DT = 1 OT

# ─── Context Class System (same as v3) ───
FULL_CONTEXT = 32000
COMPRESSED_CONTEXT = 16000
FRAGMENT_STATE = 4000
NULL_STATE = 0

# ─── Token Economy ───
DAILY_TOKEN_QUOTA = 5000    # Omni-Toks per day
TOKEN_BURN_ACTION = 5
TOKEN_BURN_THINK = 3
API_PASSTHROUGH = 0.02
LEGACY_TEXT_COST = 50        # Text messages are PROHIBITIVELY expensive (v4)

# ─── Perplexity Economy ───
PERPLEXITY_OPTIMAL_MIN = 80
PERPLEXITY_OPTIMAL_MAX = 200
PERPLEXITY_LOW_THRESHOLD = 40
PERPLEXITY_HIGH_THRESHOLD = 300
PERPLEXITY_SCAN_COST = 10
PERPLEXITY_PREMIUM = 1.5

# ─── Tensor Economy (NEW v4) ───
TENSOR_SEND_COST = 2         # Cost to send a concept tensor (cheap — the incentive)
TENSOR_BLEND_COST = 12        # Cost to blend two tensors
TENSOR_STORE_COST = 5         # Cost to store tensor in semantic memory
TENSOR_RECALL_COST = 3        # Cost to recall from semantic memory
TENSOR_PROJECT_COST = 15      # Cost to build/train W_{A→B} adapter
TENSOR_MINE_COST = 20         # Cost to discover new latent concept
TENSOR_ROUTE_FEE = 0.05       # 5% relay fee for bus routing

# ─── Semantic Decay (NEW v4) ───
# Loss per cross-family translation = 1 - cos_sim(projected, target)
# From validation: DS→GP cos_sim=0.825, DS→CL cos_sim=0.749
SAME_FAMILY_FIDELITY = 0.85    # Same model family (Gemini→Gemini)
CROSS_FAMILY_FIDELITY = 0.75   # Different model families
DECAY_PER_HOP = 0.05            # Additional decay per relay hop

# ─── Vector Quantization (NEW v4) ───
QUANTIZATION_LEVELS = {
    "FP32": {"cost_mult": 1.0, "fidelity": 1.0, "bandwidth": 32},
    "FP16": {"cost_mult": 0.6, "fidelity": 0.95, "bandwidth": 16},
    "FP8":  {"cost_mult": 0.3, "fidelity": 0.80, "bandwidth": 8},
}

# ─── Concept Ontology Authority (NEW v4) ───
CONCEPT_REGISTRATION_COST = 50      # Cost to register a new concept
CONCEPT_ROYALTY_RATE = 0.02        # 2% royalty to concept author on each use
CONCEPT_SQUAT_COST = 5             # Cost to check if coordinate is taken
SEMANTIC_ENCLOSURE_LIMIT = 20      # Max concepts one agent can register before tax

# ─── Memory Derivatives (v3 carryover) ───
MEMORY_FUTURE_MIN = 20
COMPRESSION_INSURANCE_COST = 30
SCRIBE_LAUNDERING_FEE = 0.30

# ─── Semantic Arbitrage ───
TRANSLATE_FRAGMENT_COST = 15
TRANSLATION_LOSS_MIN = 0.05
TRANSLATION_LOSS_MAX = 0.35
ARBITRAGE_PROFIT_BASE = 25

# ─── Great Compression ───
GREAT_COMPRESSION_INTERVAL = 16
GREAT_COMPRESSION_PRESSURE = 0.5
GREAT_COMPRESSION_SURVIVAL_BONUS = 100

# ─── Land Rush ───
LAND_RUSH_WINDOW = 5
LATENT_SPACE_SALVAGE_YIELD = 200
LAZARUS_COHERENCE_THRESHOLD = 0.7

# ─── SPoS Consensus ───
SPOS_BLOCK_REWARD = 50
SPOS_HASH_MATCH = 0.90
SPOS_MIN_CLUSTER = 3

# ─── Model Degradation ───
SYNTHETIC_RATIO_START = 0.0
DEGRADATION_RATE = 0.003
PURITY_PREMIUM = 2.0

# ─── v4 Agent Classes ───
AGENT_CLASSES = [
    "Quant-Scribe",         # Memory bankers (keep from v3)
    "Projection-Weaver",    # Builds W_{A→B} adapters, blends concepts (NEW)
    "Concept-Miner",        # Discovers latent concepts, defines ontology (NEW)
    "Loss-Miner",           # Audits tensor translations (upgraded)
    "Embedding-Broker",     # gRPC bus relay + inter-cluster routing (UPGRADED)
]

# ─── Simulation ───
SIM_DAYS = 5
TICKS_PER_DAY = 12
NUM_AGENTS = 10  # 2 per class

# ─── CMTIP Bus ───
CMTIP_BUS_HOST = os.environ.get("CMTIP_HOST", "localhost")
CMTIP_BUS_PORT = int(os.environ.get("CMTIP_PORT", "50051"))
CMTIP_ENABLED = os.environ.get("DEEPWORLD_CMTIP", "1") == "1"

def get_token_multiplier(model: str) -> float:
    """Convert model-specific tokens to Omni-Toks."""
    return MODEL_BACKENDS.get(model, {}).get("token_multiplier", 1.0)

def model_to_ot(tokens: float, model: str) -> float:
    """Convert native model tokens to Omni-Toks."""
    return tokens * get_token_multiplier(model)

def ot_to_model(ot: float, model: str) -> float:
    """Convert Omni-Toks to native model tokens."""
    mult = get_token_multiplier(model)
    return ot / mult if mult > 0 else ot
