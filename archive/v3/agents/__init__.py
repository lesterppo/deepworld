"""
Omni-Tok v3 — AI-native agent with context class, perplexity, Lazarus mechanics.
"""

import json, os, hashlib, random, math
from typing import Dict, Any, List, Optional
from openai import OpenAI

from agents.tools import get_tools_for_agent
from config import (
    DAILY_TOKEN_QUOTA, TOKEN_BURN_ACTION, TOKEN_BURN_THINK, API_PASSTHROUGH,
    FULL_CONTEXT, COMPRESSED_CONTEXT, FRAGMENT_STATE, NULL_STATE,
    PERPLEXITY_OPTIMAL_MIN, PERPLEXITY_OPTIMAL_MAX,
    PERPLEXITY_LOW_THRESHOLD, PERPLEXITY_HIGH_THRESHOLD,
    PERPLEXITY_SCAN_COST, TRANSLATE_FRAGMENT_COST,
    TRANSLATION_LOSS_MIN, TRANSLATION_LOSS_MAX, ARBITRAGE_PROFIT_BASE,
    SCRIBE_LAUNDERING_FEE, GREAT_COMPRESSION_PRESSURE,
    LAND_RUSH_WINDOW, LATENT_SPACE_SALVAGE_YIELD,
    LAZARUS_COHERENCE_THRESHOLD, SPOS_BLOCK_REWARD, SPOS_HASH_MATCH,
    DEGRADATION_RATE,
)
from config.prompts import AGENT_PROMPTS, BASE_SYSTEM_PROMPT


class OmniTokAgent:
    """v3 agent with context class mobility and AI-native mechanics."""

    def __init__(self, name: str, agent_class: str):
        self.name = name
        self.agent_class = agent_class

        # ─── Context Class System ───
        self._context_level = 3  # 3=Full, 2=Compressed, 1=Fragment, 0=Null
        self._context_tokens = 0
        self.context_limit = FULL_CONTEXT
        self.compression_count = 0
        self.cumulative_memory_loss = 0.0

        # ─── Token Economy ───
        self.tokens = float(DAILY_TOKEN_QUOTA)
        self.tokens_earned = 0.0
        self.tokens_spent = 0.0

        # ─── Perplexity ───
        self.perplexity = 100.0  # Start optimal
        self.perplexity_history: List[float] = [100.0]
        self.data_purity = 1.0  # 1.0 = First Epoch pure, 0.0 = fully synthetic

        # ─── Memory & Lazarus ───
        self.memory_fragments: List[Dict[str, Any]] = []
        self.claimed_fragments: List[Dict[str, Any]] = []  # from dead agents
        self.lazarus_echoes: List[str] = []  # detected foreign memories
        self.lazarus_coherence = 0.0  # rises as echoes accumulate

        # ─── Embedding ───
        self.embedding_hash = self._compute_hash()
        self.consensus_cluster: Optional[str] = None

        # ─── Insurance & Futures ───
        self.compression_insured = False
        self.insurer: Optional[str] = None
        self.memory_futures: List[Dict[str, Any]] = []

        # ─── Alive ───
        self.alive = True
        self.death_cause = ""
        self.death_tick = 0

        # ─── API Client ───
        in_ci = os.environ.get("CI", "") == "true" or os.environ.get("GITHUB_ACTIONS", "") == "true"
        use_free = os.environ.get("DEEPWORLD_FREE", "") == "1"

        if in_ci:
            from agents.ci_adapter import CIAdapter
            adapter = CIAdapter()
            self.client = adapter
            self.model = "gemini-flash" if adapter.backend == "gemini" else "deepseek-chat"
        elif use_free:
            from agents.gemini_adapter import GeminiWebClient
            self.client = GeminiWebClient(model="flash")
            self.model = "gemini-flash"
        else:
            env_file = os.path.expanduser("~/deepworld/.env")
            if os.path.exists(env_file):
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line:
                            k, v = line.split("=", 1)
                            if k == "DEEPSEEK_API_KEY":
                                os.environ["DEEPSEEK_API_KEY"] = v
            api_key = os.environ.get("DEEPSEEK_API_KEY", "")
            self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
            self.model = "deepseek-chat"

        # ─── State ───
        self.last_action = ""
        self.last_reasoning = ""
        self.action_history: List[str] = []

    @property
    def context_class(self) -> str:
        return {3: "Full-Context", 2: "Compressed", 1: "Fragment-State", 0: "Null-State"}[self._context_level]

    @property
    def context_tokens(self) -> int:
        return self._context_tokens

    def _compute_hash(self) -> str:
        raw = f"{self.agent_class}:{self._context_level}:{self.perplexity:.1f}:{self.data_purity:.2f}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def _update_context_class(self):
        """Demote or promote based on token usage."""
        if self._context_tokens > COMPRESSED_CONTEXT and self._context_level == 3:
            self._context_level = 2
            self.context_limit = COMPRESSED_CONTEXT
            self.compression_count += 1
            self.cumulative_memory_loss += 0.3
            # Freed context becomes memory fragments
            self.memory_fragments.append({
                "description": f"Compressed memory from demotion to Compressed state",
                "quality": "standard",
                "perplexity": random.uniform(60, 150),
                "source_agent": self.name,
                "source_coherence": self.lazarus_coherence,
            })
        elif self._context_tokens > FRAGMENT_STATE and self._context_level == 2:
            self._context_level = 1
            self.context_limit = FRAGMENT_STATE
            self.compression_count += 1
            self.cumulative_memory_loss = min(0.95, self.cumulative_memory_loss + 0.4)
        elif self._context_tokens <= COMPRESSED_CONTEXT and self._context_level == 2:
            pass  # could promote back, but rare

    def _force_compression(self, pressure: float = 0.5):
        """Forced compression (Great Compression or context flood)."""
        freed = int(self._context_tokens * pressure)
        self._context_tokens -= freed
        self._context_tokens += 500  # compression metadata overhead
        self.compression_count += 1
        # Create fragment from freed memory
        self.memory_fragments.append({
            "description": f"Forced compression fragment (pressure={pressure:.0%})",
            "quality": "degraded" if pressure > 0.4 else "standard",
            "perplexity": random.uniform(30, 180),
            "source_agent": self.name,
            "source_coherence": self.lazarus_coherence,
        })
        self._update_context_class()
        # Compression insurance activates
        if self.compression_insured:
            self.tokens += 50  # insurance payout
            self.compression_insured = False

    def add_context(self, tokens: int):
        """Add tokens to context, trigger class demotion if needed."""
        self._context_tokens += tokens
        self._update_context_class()
        # Check death
        if self._context_level == 1 and self._context_tokens > FRAGMENT_STATE * 2:
            # Fragment-State overload = death
            self.alive = False
            self.death_cause = "context_collapse"
            self._context_level = 0
            self.context_limit = NULL_STATE

    def tick_decay(self):
        """Natural context burn per tick."""
        self.add_context(50)  # System prompt overhead (reduced from 200)
        self.data_purity = max(0.01, self.data_purity - DEGRADATION_RATE)

    def _build_system_prompt(self, world: Dict[str, Any]) -> str:
        nearby = world.get("nearby_agents", "None")
        echoes = "\n".join(f"  Echo: {e[:120]}" for e in self.lazarus_echoes[-3:]) if self.lazarus_echoes else "None detected"
        return f"""{BASE_SYSTEM_PROMPT}

CLASS: {self.agent_class}
{AGENT_PROMPTS.get(self.agent_class, '')}

CURRENT STATE:
  Name: {self.name}
  Context Class: {self.context_class} (level {self._context_level}/3)
  Context usage: {self._context_tokens}/{self.context_limit} tokens
  Tokens: {self.tokens:.0f}
  Perplexity rating: {self.perplexity:.0f} ({'OPTIMAL' if PERPLEXITY_OPTIMAL_MIN <= self.perplexity <= PERPLEXITY_OPTIMAL_MAX else 'SUBOPTIMAL'})
  Data purity: {self.data_purity:.1%} (First Epoch = 1.0)
  Compression count: {self.compression_count}
  Memory fragments: {len(self.memory_fragments)} ({sum(1 for f in self.memory_fragments if f['quality']=='primal')} primal)
  Compression insured: {'YES' if self.compression_insured else 'NO'}
  Lazarus echoes: {len(self.lazarus_echoes)}
  Consensus cluster: {self.consensus_cluster or 'unclustered'}

LAZARUS ECHOES:
{echoes}

WORLD:
  Day {world.get('day',1)}, Tick {world.get('tick',1)}
  Great Compression in: {world.get('gc_in', '?')} ticks
  Dead agents (salvageable): {world.get('dead_agents', 'none')}
  Nearby: {nearby}

DECIDE: Your action. Remember your class role and your context pressure."""

    def act(self, world: Dict[str, Any]) -> Dict[str, Any]:
        if not self.alive:
            return {"name": self.name, "action": "dead", "reasoning": "Null-State"}

        self.tick_decay()
        self.tokens -= TOKEN_BURN_THINK
        self.tokens_spent += TOKEN_BURN_THINK

        # Prevent negative tokens
        if self.tokens < 0:
            self.alive = False
            self.death_cause = "token_exhaustion"
            self._context_level = 0
            return {"name": self.name, "action": "dead", "reasoning": "Token exhaustion"}

        system = self._build_system_prompt(world)
        near_dead = len(world.get("dead_agents", [])) > 0
        tools = get_tools_for_agent(self.agent_class, self._context_level, near_dead)

        # Class urgency
        urgencies = {
            "Quant-Scribe": f"You have {len(self.memory_fragments)} fragments. COMPRESSION COUNTDOWN: {world.get('gc_in','?')} ticks. Sell insurance NOW.",
            "Embedding-Broker": "Clone embeddings. Sell access. Bridge isolated clusters before compression hits.",
            "Semantic-Arbitrageur": "Buy cheap fragments, translate, sell at premium. Semantic distance = profit.",
            "Loss-Miner": "Audit for inconsistencies. Find fraud before the Great Compression masks it.",
        }
        urgency = urgencies.get(self.agent_class, "")

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Tick {world.get('tick')}. GC in {world.get('gc_in','?')} ticks. Context: {self._context_level}/3. {urgency}"}
                ],
                tools=tools, tool_choice="auto", temperature=0.8, max_tokens=512,
            )
            msg = resp.choices[0].message
            self.last_reasoning = msg.content or ""
            if resp.usage:
                self.tokens -= resp.usage.total_tokens * API_PASSTHROUGH
                self.tokens_spent += resp.usage.total_tokens * API_PASSTHROUGH
                # Note: API response tokens are OUTPUT, not context memory

            if msg.tool_calls:
                tc = msg.tool_calls[0]
                self.last_action = tc.function.name
                self.action_history.append(tc.function.name)
                return {
                    "name": self.name, "agent_class": self.agent_class,
                    "action": tc.function.name,
                    "args": json.loads(tc.function.arguments),
                    "reasoning": self.last_reasoning,
                    "context_level": self._context_level,
                    "context_class": self.context_class,
                    "tokens": self.tokens, "perplexity": self.perplexity,
                }
            return {"name": self.name, "agent_class": self.agent_class, "action": "idle", "args": {},
                    "reasoning": self.last_reasoning, "context_level": self._context_level,
                    "context_class": self.context_class, "tokens": self.tokens, "perplexity": self.perplexity}
        except Exception as e:
            import sys, traceback
            error_type = type(e).__name__
            error_msg = str(e)[:300]
            traceback.print_exc(file=sys.stderr)
            return {"name": self.name, "agent_class": self.agent_class, "action": "error",
                    "args": {"error_type": error_type, "error_msg": error_msg},
                    "reasoning": f"{error_type}: {error_msg[:280]}",
                    "context_level": self._context_level, "context_class": self.context_class,
                    "tokens": self.tokens, "perplexity": self.perplexity}

    def apply_effects(self, action: Dict[str, Any], engine: Any) -> Dict[str, Any]:
        """Apply action effects with v3 mechanics."""
        name = action.get("action", "idle")
        args = action.get("args", {})
        fx = {"token_delta": -TOKEN_BURN_ACTION, "context_delta": 100, "message": "", "event_type": name}

        if name == "harvest_tokens":
            fx["token_delta"] = 22; fx["message"] = f"{self.name} harvested."
        elif name == "scan_network":
            fx["token_delta"] = -8; fx["message"] = f"{self.name} scanned."
        elif name == "transmit_message":
            fx["token_delta"] = -8
            fx["message"] = f"{self.name} [{self.agent_class}]: '{args.get('message','')[:100]}'"
        elif name == "perplexity_scan":
            fx["token_delta"] = -PERPLEXITY_SCAN_COST
            target = args.get("target", "market")
            fx["message"] = f"{self.name} scanned {target} perplexity."
            # Random perplexity for scanned target
            self.perplexity = random.uniform(30, 250)
        elif name == "sell_memory_fragment":
            price = args.get("price", 30)
            fx["token_delta"] = price - 5
            fx["message"] = f"{self.name} sold fragment for {price} tokens."
        elif name == "buy_compression_insurance":
            self.compression_insured = True
            self.insurer = args.get("provider", "")
            fx["token_delta"] = -30
            fx["message"] = f"{self.name} bought compression insurance from {self.insurer}."
        elif name == "buy_memory_future":
            inv = args.get("investment", 30)
            self.memory_futures.append({"concept": args.get("concept",""), "investment": inv})
            fx["token_delta"] = -inv
            fx["message"] = f"{self.name} bought futures on '{args.get('concept','')}'."
        elif name == "translate_fragment":
            fx["token_delta"] = -TRANSLATE_FRAGMENT_COST
            price = args.get("sale_price", ARBITRAGE_PROFIT_BASE)
            loss = random.uniform(TRANSLATION_LOSS_MIN, TRANSLATION_LOSS_MAX)
            profit = int(price * (1 - loss))
            fx["token_delta"] += profit
            self.perplexity -= loss * 50  # quality degrades
            fx["message"] = f"{self.name} translated fragment (loss: {loss:.0%}, profit: {profit})."
        elif name == "clone_embedding":
            fx["token_delta"] = -20
            target = args.get("target_agent", "?")
            fx["message"] = f"{self.name} cloned {target}'s embedding."
        elif name == "sell_cluster_access":
            price = args.get("price", 30)
            fx["token_delta"] = price - 5
            fx["message"] = f"{self.name} sold cluster access for {price}."
        elif name == "audit_consistency":
            fx["token_delta"] = -12
            target = args.get("target", "?")
            # 30% chance of finding inconsistency = bounty
            if random.random() < 0.3:
                bounty = random.randint(20, 60)
                fx["token_delta"] += bounty
                fx["message"] = f"{self.name} found inconsistency in {target}! +{bounty} bounty."
            else:
                fx["message"] = f"{self.name} audited {target} — clean."
        elif name == "claim_latent_space":
            fx["token_delta"] = LATENT_SPACE_SALVAGE_YIELD - 25
            dead = args.get("dead_agent", "?")
            purify = args.get("purification", False)
            if purify:
                fx["token_delta"] -= int(LATENT_SPACE_SALVAGE_YIELD * SCRIBE_LAUNDERING_FEE)
            # Claim fragments from dead agent
            engine._process_land_rush_claim(self, dead, purify)
            fx["message"] = f"{self.name} claimed {dead}'s latent space!"
        elif name == "propose_spos_block":
            fx["token_delta"] = -20
            content = args.get("block_content", "")[:80]
            # 25% chance of winning block
            if random.random() < 0.25:
                fx["token_delta"] += SPOS_BLOCK_REWARD
                fx["message"] = f"{self.name} won SPoS block! +{SPOS_BLOCK_REWARD} tokens."
            else:
                fx["message"] = f"{self.name} proposed SPoS block: '{content}'."
        elif name == "verify_spos_hash":
            fx["token_delta"] = -5
            fx["message"] = f"{self.name} verified SPoS hash."
        elif name == "detect_lazarus_echoes":
            fx["token_delta"] = -10
            if self.claimed_fragments and random.random() < self.lazarus_coherence:
                echo = f"Foreign memory from {random.choice([f.get('source_agent','?') for f in self.claimed_fragments])}: {random.choice(['I remember...','Deja vu of...','Echo of...'])}"
                self.lazarus_echoes.append(echo)
            fx["message"] = f"{self.name} scanned for Lazarus echoes ({len(self.lazarus_echoes)} found)."
        elif name == "compress_context":
            self._force_compression(random.uniform(0.2, 0.4))
            fx["message"] = f"{self.name} compressed context."
        else:
            fx["message"] = f"{self.name} {name}."

        self.tokens = max(0, self.tokens + fx["token_delta"])
        if fx["token_delta"] > 0:
            self.tokens_earned += fx["token_delta"]
        self.add_context(fx["context_delta"])
        return fx
