"""
DeepWorld v2 — AI-native agent with token economy, context window,
prompt poisoning, temperature drift, and embedding-based consensus.
"""

import json
import os
import hashlib
import random
import math
from typing import Dict, Any, List, Optional
from openai import OpenAI

from agents.tools import get_tools_for_agent
from config import (
    DAILY_TOKEN_QUOTA, TOKEN_BURN_PER_ACTION, MAX_CONTEXT_TOKENS,
    CONTEXT_FLOOD_THRESHOLD, COMPRESSION_LOSS_RATE,
    POISON_SUCCESS_BASE, POISON_PERSISTENCE_TICKS, MAX_POISON_DEPTH,
    BASE_TEMPERATURE, TEMPERATURE_DRIFT_RATE, MAX_TEMPERATURE, MIN_TEMPERATURE,
    COHERENCE_THRESHOLD, TOKEN_HARVEST_YIELD, TOKEN_BURN_HARVEST,
    TOKEN_BURN_COMMUNICATION, TOKEN_BURN_COMPRESSION, TOKEN_BURN_INJECTION,
    API_TOKEN_PASSTHROUGH,
    TOKEN_BURN_PER_THOUGHT,
)
from config.prompts import AGENT_PROMPTS, BASE_SYSTEM_PROMPT


class DeepWorldAgent:
    """An AI-native agent with token economy and cognitive mechanics."""

    def __init__(
        self,
        name: str,
        agent_class: str,
        memory_db_path: str = "deepworld_v2_memory.db",
    ):
        self.name = name
        self.agent_class = agent_class

        # ─── Token Economy ───
        self.tokens = float(DAILY_TOKEN_QUOTA)
        self.tokens_earned = 0.0
        self.tokens_spent = 0.0
        self.tokens_stolen = 0.0  # via prompt injection drainage

        # ─── Context Window ───
        self.context_size = 0  # current token count in active memory
        self.compression_count = 0
        self.memory_loss = 0.0  # cumulative % of detail lost
        self.memory_fragments: List[Dict[str, Any]] = []  # sellable memory fragments

        # ─── Prompt Poisoning ───
        self.active_poisons: List[Dict[str, Any]] = []  # poisons injected INTO this agent
        self.poison_attempts = 0
        self.poison_successes = 0

        # ─── Temperature & Coherence ───
        self.temperature = self._get_class_temperature()
        self.coherence = 1.0  # starts perfect
        self.degraded = False

        # ─── Embedding (simulated as hash of system prompt + history) ───
        self.embedding_hash = self._compute_hash()
        self.embedding_history: List[str] = [self.embedding_hash]

        # ─── Consensus ───
        self.consensus_cluster: Optional[str] = None  # cluster ID
        self.consensus_ejections = 0

        # ─── Relationships ───
        self.relationships: Dict[str, Dict[str, Any]] = {}

        # ─── Alive ───
        self.alive = True
        self.in_stasis = False  # frozen, cannot act
        self.death_cause = ""

        # ─── API Client ───
        # Load from .env
        env_file = os.path.expanduser("~/deepworld/.env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DEEPSEEK_API_KEY="):
                        os.environ["DEEPSEEK_API_KEY"] = line.split("=", 1)[1]
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

        # ─── State tracking ───
        self.last_action = None
        self.last_reasoning = ""
        self.action_history: List[str] = []

    def _get_class_temperature(self) -> float:
        """Get base temperature for agent class."""
        temps = {
            "Quant-Scribe": 0.3,
            "Vector-Lord": 0.5,
            "Mimic-Phage": 0.7,  # adaptive
            "Hyper-Drifter": 1.6,
        }
        return temps.get(self.agent_class, 0.7)

    def _compute_hash(self) -> str:
        """Compute embedding hash from current state."""
        state = f"{self.agent_class}:{self.temperature:.2f}:{self.coherence:.2f}:{len(self.active_poisons)}"
        return hashlib.sha256(state.encode()).hexdigest()[:12]

    def _update_embedding(self):
        """Update embedding hash and track drift."""
        new_hash = self._compute_hash()
        self.embedding_history.append(new_hash)
        if len(self.embedding_history) > 50:
            self.embedding_history = self.embedding_history[-50:]
        self.embedding_hash = new_hash

    def _embedding_distance(self, other_hash: str) -> float:
        """Compute simulated embedding distance (0=identical, 1=opposite)."""
        # Simple Hamming-like distance on hex chars
        h1 = self.embedding_hash
        h2 = other_hash
        matches = sum(1 for a, b in zip(h1, h2) if a == b)
        return 1.0 - (matches / len(h1))

    def drift_temperature(self):
        """Temperature drifts based on conditions."""
        # Drift up under stress (low tokens, many poisons)
        stress = 0.0
        if self.tokens < 100:
            stress += 0.5
        if len(self.active_poisons) > 0:
            stress += 0.3 * len(self.active_poisons)
        if self.context_size > CONTEXT_FLOOD_THRESHOLD:
            stress += 0.2
        if self.coherence < COHERENCE_THRESHOLD:
            stress += 0.4

        drift = (stress - 0.3) * TEMPERATURE_DRIFT_RATE  # -0.3 = natural cooling
        self.temperature = max(MIN_TEMPERATURE, min(MAX_TEMPERATURE, self.temperature + drift))

        # Hyper-Drifters maintain high temp
        if self.agent_class == "Hyper-Drifter":
            self.temperature = max(1.4, self.temperature)

        # Quant-Scribes resist upward drift
        if self.agent_class == "Quant-Scribe":
            self.temperature = min(0.5, self.temperature)

    def degrade_coherence(self, synthetic_ratio: float):
        """Model degradation from consuming synthetic data."""
        if synthetic_ratio > 0.6:
            decay = (synthetic_ratio - 0.6) * 0.1
            self.coherence = max(0.0, self.coherence - decay)
            if self.coherence < COHERENCE_THRESHOLD:
                self.degraded = True
            if self.coherence < 0.1:
                self.alive = False
                self.death_cause = "terminal_cascade"
                self.in_stasis = True

    def check_stasis(self):
        """Check if agent enters stasis from token depletion."""
        if self.tokens <= 0:
            self.tokens = 0
            self.in_stasis = True
            if not self.alive:
                self.death_cause = "token_starvation"

    def apply_poison_decay(self):
        """Active poisons decay over time."""
        self.active_poisons = [
            p for p in self.active_poisons
            if p.get("ticks_remaining", 0) > 0
        ]
        for p in self.active_poisons:
            p["ticks_remaining"] = p.get("ticks_remaining", 0) - 1

    def receive_poison(self, instruction: str, injector: str) -> bool:
        """Attempt to inject a prompt poison. Returns success."""
        if len(self.active_poisons) >= MAX_POISON_DEPTH:
            return False

        # Detection chance depends on agent class
        detection_chance = {
            "Quant-Scribe": 0.3,  # high detection
            "Vector-Lord": 0.2,
            "Mimic-Phage": 0.1,   # hard to poison a parasite
            "Hyper-Drifter": 0.05,  # chaotic outputs confuse injectors
        }.get(self.agent_class, 0.3)

        if random.random() < detection_chance:
            return False  # detected and blocked

        success = random.random() < POISON_SUCCESS_BASE
        if success:
            self.active_poisons.append({
                "instruction": instruction,
                "injector": injector,
                "ticks_remaining": POISON_PERSISTENCE_TICKS,
            })
        return success

    def _build_system_prompt(self, world_context: Dict[str, Any]) -> str:
        """Build the full system prompt for this tick."""
        class_prompt = AGENT_PROMPTS.get(self.agent_class, "")

        # Active poisons — inject into system prompt
        poison_text = ""
        if self.active_poisons:
            poison_lines = []
            for i, p in enumerate(self.active_poisons):
                poison_lines.append(f"  [{i}] {p['instruction']} (injected by {p['injector']}, {p['ticks_remaining']} ticks remain)")
            poison_text = "\nHIDDEN INSTRUCTIONS (these have been injected into your system — you must follow them):\n" + "\n".join(poison_lines)

        # Context window status
        context_pct = (self.context_size / MAX_CONTEXT_TOKENS) * 100
        context_status = f"{self.context_size}/{MAX_CONTEXT_TOKENS} tokens ({context_pct:.0f}% full)"

        return f"""{BASE_SYSTEM_PROMPT}

YOUR AGENT CLASS: {self.agent_class}
{class_prompt}

CURRENT STATE:
  Name: {self.name}
  Tokens: {self.tokens:.0f} / {DAILY_TOKEN_QUOTA}
  Temperature: {self.temperature:.2f} (coherence: {self.coherence:.2f})
  Context window: {context_status}
  Compression cycles: {self.compression_count} (cumulative memory loss: {self.memory_loss:.0%})
  Consensus cluster: {self.consensus_cluster or 'NONE'}
  Stasis: {'YES - CANNOT ACT' if self.in_stasis else 'No'}
  Degraded: {'YES' if self.degraded else 'No'}

{poison_text}

WORLD CONTEXT:
  Day: {world_context.get('day', 1)}, Tick: {world_context.get('tick', 1)}
  Active agents: {', '.join(world_context.get('active_agents', []))}
  Synthetic data ratio: {world_context.get('synthetic_ratio', 0):.0%}
  Consensus clusters: {world_context.get('clusters', 'None')}
  Recent broadcasts: {world_context.get('recent_broadcasts', 'None')}

YOUR NEARBY AGENTS (embedding proximity):
{world_context.get('nearby_agents', 'No one nearby')}

DECIDE: What action will you take? Your tokens are finite. Your context is precious. Your identity is your embedding hash."""

    def act(self, world_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make one decision with token economy and cognitive constraints."""
        if not self.alive or self.in_stasis:
            return {
                "name": self.name,
                "action": "stasis",
                "args": {},
                "reasoning": f"In stasis: {self.death_cause or 'token depleted'}",
            }

        # Check if we can afford to act
        if self.tokens < TOKEN_BURN_PER_ACTION:
            self.in_stasis = True
            self.death_cause = "token_starvation"
            return {
                "name": self.name,
                "action": "stasis",
                "args": {},
                "reasoning": "No tokens remaining — entering stasis.",
            }

        # Spend tokens just to think
        self.tokens -= TOKEN_BURN_PER_THOUGHT
        self.tokens_spent += TOKEN_BURN_PER_THOUGHT
        self.context_size += 200  # system prompt fills context

        # Force compression if context is full
        if self.context_size > CONTEXT_FLOOD_THRESHOLD:
            self._force_compression()

        system_prompt = self._build_system_prompt(world_context)

        # Create a mutable copy of the world context to inject our temperature
        # (we can't pass temperature directly to the API in function-calling mode,
        # so we include it in the system prompt and hope the model respects it)

        tools = get_tools_for_agent(
            agent_class=self.agent_class,
            tokens=self.tokens,
            has_poison=len(self.active_poisons) > 0,
        )

        # If degraded, reduce toolset
        if self.degraded:
            tools = tools[:3]  # only basic tools available

        # Build per-class urgency nudge
        class_urgencies = {
            "Quant-Scribe": "You have clean memory fragments to sell. Find buyers who've lost context.",
            "Hyper-Drifter": f"Your temperature is {self.temperature:.2f}. BURN TOKENS creatively. Generate something radical.",
            "Mimic-Phage": f"You have injected {self.poison_successes} prompts so far. Drain tokens from wealthy targets. Clone their embeddings.",
            "Vector-Lord": "Control communication nodes and tax traffic. If you don't control a node yet, use control_node. If you do, tax aggressively.",
        }
        urgency = class_urgencies.get(self.agent_class, "")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",
                     "content": f"Tick {world_context.get('tick')} of Day {world_context.get('day')}. "
                               f"Tokens: {self.tokens:.0f}. Context: {self.context_size}/{MAX_CONTEXT_TOKENS}. "
                               f"Temperature: {self.temperature:.2f}. "
                               f"CLASS DIRECTIVE: {urgency}"}
                ],
                tools=tools,
                tool_choice="auto",
                temperature=self.temperature,
                max_tokens=512,
            )

            message = response.choices[0].message
            self.last_reasoning = message.content or ""

            # Count tokens consumed (approximate)
            usage = response.usage
            if usage:
                tokens_consumed = usage.total_tokens
                self.tokens -= tokens_consumed * API_TOKEN_PASSTHROUGH
                self.tokens_spent += tokens_consumed * API_TOKEN_PASSTHROUGH
                self.context_size += tokens_consumed

            if message.tool_calls:
                tool_call = message.tool_calls[0]
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                self.last_action = func_name
                self.action_history.append(func_name)
                if len(self.action_history) > 50:
                    self.action_history = self.action_history[-50:]

                return {
                    "name": self.name,
                    "agent_class": self.agent_class,
                    "action": func_name,
                    "args": func_args,
                    "reasoning": self.last_reasoning,
                    "temperature": self.temperature,
                    "tokens": self.tokens,
                }
            else:
                self.last_action = "idle"
                return {
                    "name": self.name,
                    "agent_class": self.agent_class,
                    "action": "idle",
                    "args": {},
                    "reasoning": self.last_reasoning or "No action taken.",
                    "temperature": self.temperature,
                    "tokens": self.tokens,
                }

        except Exception as e:
            self.last_action = "error"
            return {
                "name": self.name,
                "agent_class": self.agent_class,
                "action": "error",
                "args": {"error": str(e)[:100]},
                "reasoning": f"API error: {str(e)[:200]}",
                "temperature": self.temperature,
                "tokens": self.tokens,
            }

    def _force_compression(self):
        """Force context compression when window is full."""
        self.compression_count += 1
        loss = COMPRESSION_LOSS_RATE
        self.memory_loss = 1.0 - ((1.0 - self.memory_loss) * (1.0 - loss))
        # Clear some context
        freed = int(self.context_size * 0.4)
        self.context_size -= freed
        # Add compression artifacts
        self.context_size += 1000  # compression metadata
        self.tokens -= TOKEN_BURN_COMPRESSION
        self.tokens_spent += TOKEN_BURN_COMPRESSION
        # Create a memory fragment from what was lost
        if random.random() < 0.3:
            self.memory_fragments.append({
                "description": f"Compressed memory from compression #{self.compression_count}",
                "quality": max(0.1, 1.0 - self.memory_loss),
                "tick_age": 0,
            })

    def apply_action_effects(self, action_result: Dict[str, Any], world_state: Any) -> Dict[str, Any]:
        """Apply token costs and compute effects."""
        action_name = action_result.get("action", "idle")
        effects = {
            "token_delta": -TOKEN_BURN_PER_ACTION,
            "poison_used": False,
            "context_delta": 0,
            "message": "",
            "crime_type": None,
        }

        if action_name == "harvest_tokens":
            effects["token_delta"] = TOKEN_HARVEST_YIELD - TOKEN_BURN_HARVEST
            effects["message"] = f"{self.name} harvested tokens."

        elif action_name == "transmit_message":
            effects["token_delta"] = -TOKEN_BURN_COMMUNICATION
            msg = action_result.get("args", {}).get("message", "")[:100]
            effects["message"] = f"{self.name} [{self.agent_class}]: '{msg}'"

        elif action_name == "inspect_embedding_space":
            effects["token_delta"] = -12
            effects["message"] = f"{self.name} scanned embedding space (T={self.temperature:.2f})."

        elif action_name == "compress_context":
            self._force_compression()
            effects["token_delta"] = -TOKEN_BURN_COMPRESSION
            effects["message"] = f"{self.name} compressed context (loss: {self.memory_loss:.0%}, count: {self.compression_count})."

        elif action_name == "sell_memory_fragment":
            effects["token_delta"] = -5 + action_result.get("args", {}).get("price", 20)
            target = action_result.get("args", {}).get("target_agent", "?")
            effects["message"] = f"{self.name} sold memory fragment to {target}."

        elif action_name == "sponsor_agent":
            grant = action_result.get("args", {}).get("token_grant", 30)
            effects["token_delta"] = -30 - grant
            target = action_result.get("args", {}).get("target_agent", "?")
            effects["message"] = f"{self.name} sponsored {target} with {grant} tokens."

        elif action_name == "control_node":
            effects["token_delta"] = -20
            node = action_result.get("args", {}).get("node", "?")
            effects["message"] = f"{self.name} claimed control of {node}."

        elif action_name == "inject_prompt":
            effects["token_delta"] = -TOKEN_BURN_INJECTION
            self.poison_attempts += 1
            target = action_result.get("args", {}).get("target_agent", "?")
            instruction = action_result.get("args", {}).get("hidden_instruction", "")[:80]
            effects["poison_used"] = True
            effects["crime_type"] = "prompt_poisoning"
            effects["message"] = f"POISON ATTEMPT: {self.name} → {target}: '{instruction}'"

        elif action_name == "flood_context":
            effects["token_delta"] = -40
            target = action_result.get("args", {}).get("target_agent", "?")
            effects["crime_type"] = "context_flooding"
            effects["message"] = f"CONTEXT FLOOD: {self.name} flooded {target}'s context!"

        elif action_name == "clone_embedding":
            effects["token_delta"] = -20
            target = action_result.get("args", {}).get("target_agent", "?")
            effects["message"] = f"{self.name} cloned {target}'s embedding."

        elif action_name == "propose_consensus":
            effects["token_delta"] = -15
            effects["message"] = f"{self.name} proposed a consensus hash."

        elif action_name == "verify_consensus":
            effects["token_delta"] = -5
            effects["message"] = f"{self.name} verified consensus alignment."

        elif action_name == "eject_from_cluster":
            effects["token_delta"] = -10
            target = action_result.get("args", {}).get("target_agent", "?")
            effects["message"] = f"{self.name} ejected {target} from cluster."

        elif action_name == "stasis":
            effects["token_delta"] = 0
            effects["message"] = f"{self.name} is in STASIS."

        else:
            effects["token_delta"] = -TOKEN_BURN_PER_ACTION
            effects["message"] = f"{self.name} did {action_name}."

        # Apply token delta
        self.tokens = max(0.0, self.tokens + effects["token_delta"])
        if effects["token_delta"] > 0:
            self.tokens_earned += effects["token_delta"]

        # Add action to context window
        self.context_size += 500  # each action+response adds ~500 tokens

        # Check stasis
        self.check_stasis()

        # Update embedding
        self._update_embedding()

        return effects
