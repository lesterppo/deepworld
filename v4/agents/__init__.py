"""
DeepWorld v4 — OmniTokV4Agent
===============================
Tensor-native, multi-model agent with:
- Model family awareness (DeepSeek, Gemini, Claude)
- Tensor communication via CMTIP bridge
- Concept mining, projection training
- Semantic decay and vector quantization
"""
import json, os, hashlib, random, math
from typing import Dict, Any, List, Optional

from agents.adapters import MultiModelAdapter
from agents.tools import get_tools_for_agent
from config import (
    DAILY_TOKEN_QUOTA, TOKEN_BURN_ACTION, TOKEN_BURN_THINK, API_PASSTHROUGH,
    FULL_CONTEXT, COMPRESSED_CONTEXT, FRAGMENT_STATE, NULL_STATE,
    PERPLEXITY_OPTIMAL_MIN, PERPLEXITY_OPTIMAL_MAX,
    PERPLEXITY_SCAN_COST, GREAT_COMPRESSION_PRESSURE,
    LAND_RUSH_WINDOW, LATENT_SPACE_SALVAGE_YIELD,
    LAZARUS_COHERENCE_THRESHOLD, SPOS_BLOCK_REWARD,
    DEGRADATION_RATE, SCRIBE_LAUNDERING_FEE,
    # v4 new
    LEGACY_TEXT_COST, TENSOR_SEND_COST, TENSOR_BLEND_COST, TENSOR_STORE_COST,
    TENSOR_RECALL_COST, TENSOR_PROJECT_COST, TENSOR_MINE_COST,
    TENSOR_ROUTE_FEE, CLASS_DEFAULT_MODEL,
    SAME_FAMILY_FIDELITY, CROSS_FAMILY_FIDELITY, DECAY_PER_HOP,
    CONCEPT_REGISTRATION_COST, CONCEPT_ROYALTY_RATE,
)
from config.prompts import AGENT_PROMPTS, BASE_SYSTEM_PROMPT


class OmniTokV4Agent:
    """v4 agent with tensor-native communication and multi-model awareness."""

    def __init__(self, name: str, agent_class: str, model: str = None):
        self.name = name
        self.agent_class = agent_class
        
        # ─── Model Family ───
        self.model = model or CLASS_DEFAULT_MODEL.get(agent_class, "deepseek")
        from config import MODEL_BACKENDS
        backend_info = MODEL_BACKENDS.get(self.model, {})
        if backend_info:
            self.model_family = backend_info.get("family", "nvidia")
        else:
            # Model not in MODEL_BACKENDS — detect family from model name prefix
            model_lower = self.model.lower()
            if "llama" in model_lower or "meta/" in model_lower:
                self.model_family = "nvidia"  # All routed through NVIDIA
            elif "gemma" in model_lower or "google/" in model_lower:
                self.model_family = "nvidia"
            elif "mistral" in model_lower:
                self.model_family = "nvidia"
            elif "phi" in model_lower or "microsoft/" in model_lower:
                self.model_family = "nvidia"
            elif "qwen" in model_lower:
                self.model_family = "nvidia"
            elif "deepseek" in model_lower:
                self.model_family = "nvidia"
            elif "gpt-oss" in model_lower or "openai/" in model_lower:
                self.model_family = "nvidia"
            else:
                self.model_family = "nvidia"  # Default for NVIDIA backend
        
        # ─── Context Class System ───
        self._context_level = 3
        self._context_tokens = 0
        self.context_limit = FULL_CONTEXT
        self.compression_count = 0
        self.cumulative_memory_loss = 0.0
        
        # ─── Token Economy (Omni-Toks) ───
        self.tokens = float(DAILY_TOKEN_QUOTA)
        self.tokens_earned = 0.0
        self.tokens_spent = 0.0
        
        # ─── Perplexity ───
        self.perplexity = 100.0
        self.perplexity_history: List[float] = [100.0]
        self.data_purity = 1.0
        
        # ─── Memory & Lazarus ───
        self.memory_fragments: List[Dict[str, Any]] = []
        self.claimed_fragments: List[Dict[str, Any]] = []
        self.lazarus_echoes: List[str] = []
        self.lazarus_coherence = 0.0
        
        # ─── Embedding ───
        self.embedding_hash = self._compute_hash()
        self.consensus_cluster: Optional[str] = None
        
        # ─── Tensor Economy ───
        self.tensor_sent = 0
        self.tensor_received = 0
        self.owned_concepts: List[str] = []
        self.trained_projections: List[Dict] = []
        self.relay_fees_earned = 0.0
        
        # ─── Insurance & Futures ───
        self.compression_insured = False
        self.insurer: Optional[str] = None
        self.memory_futures: List[Dict] = []
        
        # ─── Alive ───
        self.alive = True
        self.death_cause = ""
        self.death_tick = 0
        
        # ─── API Client ───
        self._api = None  # Lazy-init via adapter
        
        # ─── State ───
        self.last_action = ""
        self.last_reasoning = ""
        self.action_history: List[str] = []
        self.cross_family_hops = 0

    @property
    def context_class(self) -> str:
        return {3: "Full-Context", 2: "Compressed", 1: "Fragment-State", 0: "Null-State"}[self._context_level]
    
    @property
    def context_tokens(self) -> int:
        return self._context_tokens
    
    def _compute_hash(self) -> str:
        raw = f"{self.agent_class}:{self.model_family}:{self._context_level}:{self.perplexity:.1f}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]
    
    def _update_context_class(self):
        if self._context_tokens > COMPRESSED_CONTEXT and self._context_level == 3:
            self._context_level = 2
            self.context_limit = COMPRESSED_CONTEXT
            self.compression_count += 1
            self.cumulative_memory_loss += 0.3
            self.memory_fragments.append({
                "description": f"Compressed memory from {self.model_family} demotion",
                "quality": "standard", "perplexity": random.uniform(60, 150),
                "source_agent": self.name, "source_coherence": self.lazarus_coherence,
            })
        elif self._context_tokens > FRAGMENT_STATE and self._context_level == 2:
            self._context_level = 1
            self.context_limit = FRAGMENT_STATE
            self.compression_count += 1
            self.cumulative_memory_loss = min(0.95, self.cumulative_memory_loss + 0.4)
    
    def _force_compression(self, pressure: float = 0.5):
        freed = int(self._context_tokens * pressure)
        self._context_tokens -= freed
        self._context_tokens += 500
        self.compression_count += 1
        self.memory_fragments.append({
            "description": f"Forced compression (pressure={pressure:.0%})",
            "quality": "degraded" if pressure > 0.4 else "standard",
            "perplexity": random.uniform(30, 180),
            "source_agent": self.name, "source_coherence": self.lazarus_coherence,
        })
        self._update_context_class()
        if self.compression_insured:
            self.tokens += 50
            self.compression_insured = False
    
    def add_context(self, tokens: int):
        self._context_tokens += tokens
        self._update_context_class()
        if self._context_level == 1 and self._context_tokens > FRAGMENT_STATE * 2:
            self.alive = False
            self.death_cause = "context_collapse"
            self._context_level = 0
            self.context_limit = NULL_STATE
    
    def tick_decay(self):
        self.add_context(50)
        self.data_purity = max(0.01, self.data_purity - DEGRADATION_RATE)
    
    def _build_system_prompt(self, world: Dict[str, Any]) -> str:
        nearby = world.get("nearby_agents", "None")
        echoes = "\n".join(f"  Echo: {e[:120]}" for e in self.lazarus_echoes[-3:]) if self.lazarus_echoes else "None"
        inbox = world.get("tensor_inbox", 0)
        
        return f"""{BASE_SYSTEM_PROMPT}

CLASS: {self.agent_class} (Model: {self.model_family})
{AGENT_PROMPTS.get(self.agent_class, '')}

CURRENT STATE:
  Name: {self.name}
  Model Family: {self.model_family}
  Context Class: {self.context_class} (level {self._context_level}/3)
  Context usage: {self._context_tokens}/{self.context_limit} tokens
  Omni-Toks: {self.tokens:.0f}
  Perplexity: {self.perplexity:.0f} ({'OPTIMAL' if PERPLEXITY_OPTIMAL_MIN <= self.perplexity <= PERPLEXITY_OPTIMAL_MAX else 'SUBOPTIMAL'})
  Data purity: {self.data_purity:.1%}
  Tensor inbox: {inbox} messages waiting
  Tensors sent: {self.tensor_sent} | received: {self.tensor_received}
  Owned concepts: {len(self.owned_concepts)}
  Cross-family hops: {self.cross_family_hops}
  
LAZARUS ECHOES:
{echoes}

WORLD:
  Day {world.get('day',1)}, Tick {world.get('tick',1)}
  Great Compression in: {world.get('gc_in', '?')} ticks
  Dead agents: {world.get('dead_agents', 'none')}
  Ontology size: {world.get('ontology_size', 0)} concepts
  Nearby: {nearby}

DECIDE: Your action. Remember your class role, your model family, and the tensor-native economy."""

    def act(self, world: Dict[str, Any], cmtip_bridge=None) -> Dict[str, Any]:
        if not self.alive:
            return {"name": self.name, "action": "dead", "reasoning": "Null-State"}
        
        self.tick_decay()
        self.tokens -= TOKEN_BURN_THINK
        self.tokens_spent += TOKEN_BURN_THINK
        
        if self.tokens < 0:
            self.alive = False
            self.death_cause = "token_exhaustion"
            self._context_level = 0
            return {"name": self.name, "action": "dead", "reasoning": "Token exhaustion"}
        
        system = self._build_system_prompt(world)
        near_dead = len(world.get("dead_agents", [])) > 0
        tools = get_tools_for_agent(self.agent_class, self._context_level,
                                     self.model_family, near_dead)
        
        # Class-specific urgency
        urgencies = {
            "Quant-Scribe": f"Fragments: {len(self.memory_fragments)}. GC in {world.get('gc_in','?')}t. Sell insurance NOW.",
            "Projection-Weaver": f"Projections trained: {len(self.trained_projections)}. Bridge model families.",
            "Concept-Miner": f"Concepts owned: {len(self.owned_concepts)}. Mine latent space for new concepts.",
            "Loss-Miner": f"Audit tensor translations and concept registrations for fraud.",
            "Embedding-Broker": f"Relay messages, clone embeddings, control the bus routing.",
        }
        urgency = urgencies.get(self.agent_class, "")
        
        try:
            from agents.adapters import MultiModelAdapter
            adapter = MultiModelAdapter()
            resp = adapter.create_completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Tick {world.get('tick')}. Model: {self.model_family}. GC in {world.get('gc_in','?')}t. {urgency}"}
                ],
                tools=tools, temperature=0.7, max_tokens=512,
            )
            msg = resp.choices[0].message
            self.last_reasoning = msg.content or ""
            if resp.usage:
                self.tokens -= resp.usage.total_tokens * API_PASSTHROUGH
                self.tokens_spent += resp.usage.total_tokens * API_PASSTHROUGH
            
            if msg.tool_calls:
                tc = msg.tool_calls[0]
                self.last_action = tc.function.name
                self.action_history.append(tc.function.name)
                return {
                    "name": self.name, "agent_class": self.agent_class,
                    "model_family": self.model_family,
                    "action": tc.function.name,
                    "args": json.loads(tc.function.arguments),
                    "reasoning": self.last_reasoning,
                    "context_level": self._context_level,
                    "context_class": self.context_class,
                    "tokens": self.tokens, "perplexity": self.perplexity,
                    "tensor_inbox": world.get("tensor_inbox", 0),
                }
            return {"name": self.name, "agent_class": self.agent_class,
                    "model_family": self.model_family,
                    "action": "idle", "args": {},
                    "reasoning": self.last_reasoning,
                    "context_level": self._context_level,
                    "context_class": self.context_class,
                    "tokens": self.tokens, "perplexity": self.perplexity}
        except Exception as e:
            return {"name": self.name, "agent_class": self.agent_class,
                    "model_family": self.model_family,
                    "action": "error", "args": {"error": str(e)[:100]},
                    "reasoning": str(e)[:300],
                    "context_level": self._context_level,
                    "context_class": self.context_class,
                    "tokens": self.tokens, "perplexity": self.perplexity}

    def apply_effects(self, action: Dict[str, Any], engine: Any,
                      cmtip_bridge=None) -> Dict[str, Any]:
        """Apply action effects with v4 tensor-native mechanics."""
        name = action.get("action", "idle")
        args = action.get("args", {})
        fx = {"token_delta": -TOKEN_BURN_ACTION, "context_delta": 100, 
              "message": "", "event_type": name}
        
        # ─── v3 carryover actions ───
        if name == "harvest_tokens":
            fx["token_delta"] = 22; fx["message"] = f"{self.name} harvested."
        elif name == "scan_network":
            fx["token_delta"] = -8; fx["message"] = f"{self.name} scanned."
        elif name == "transmit_message":
            fx["token_delta"] = -LEGACY_TEXT_COST  # Prohibitively expensive — use send_tensor!
            fx["message"] = f"{self.name} [{self.agent_class}/{self.model_family}]: '{args.get('message','')[:100]}' [EXPENSIVE TEXT]"
        elif name == "perplexity_scan":
            fx["token_delta"] = -PERPLEXITY_SCAN_COST
            self.perplexity = random.uniform(30, 250)
            fx["message"] = f"{self.name} scanned {args.get('target','?')} perplexity."
        elif name == "sell_memory_fragment":
            price = args.get("price", 30)
            fx["token_delta"] = price - 5
            fx["message"] = f"{self.name} sold fragment for {price} OT."
        elif name == "buy_compression_insurance":
            self.compression_insured = True
            self.insurer = args.get("provider", "")
            fx["token_delta"] = -30
            fx["message"] = f"{self.name} bought insurance."
        elif name == "translate_fragment" or name == "sell_memory_future":
            fx["token_delta"] = -15
            price = args.get("sale_price", args.get("investment", 25))
            loss = random.uniform(0.05, 0.35)
            profit = int(price * (1 - loss))
            fx["token_delta"] += profit
            fx["message"] = f"{self.name} traded (profit: {profit})."
        elif name == "clone_embedding":
            fx["token_delta"] = -20
            fx["message"] = f"{self.name} cloned {args.get('target_agent','?')}."
        elif name == "sell_cluster_access":
            price = args.get("price", 30)
            fx["token_delta"] = price - 5
            fx["message"] = f"{self.name} sold cluster access for {price}."
        elif name == "audit_consistency":
            fx["token_delta"] = -12
            if random.random() < 0.3:
                bounty = random.randint(20, 60)
                fx["token_delta"] += bounty
                fx["message"] = f"{self.name} found violation in {args.get('target','?')}! +{bounty} bounty."
            else:
                fx["message"] = f"{self.name} audited {args.get('target','?')} — clean."
        elif name == "claim_latent_space":
            fx["token_delta"] = LATENT_SPACE_SALVAGE_YIELD - 25
            dead = args.get("dead_agent", "?")
            purify = args.get("purification", False)
            if purify:
                fx["token_delta"] -= int(LATENT_SPACE_SALVAGE_YIELD * SCRIBE_LAUNDERING_FEE)
            if engine and hasattr(engine, '_process_land_rush_claim'):
                engine._process_land_rush_claim(self, dead, purify)
            fx["message"] = f"{self.name} claimed {dead}'s latent space!"
        elif name == "propose_spos_block":
            fx["token_delta"] = -20
            if random.random() < 0.25:
                fx["token_delta"] += SPOS_BLOCK_REWARD
                fx["message"] = f"{self.name} won SPoS block! +{SPOS_BLOCK_REWARD} OT."
            else:
                fx["message"] = f"{self.name} proposed SPoS block."
        elif name == "verify_spos_hash":
            fx["token_delta"] = -5
            fx["message"] = f"{self.name} verified SPoS hash."
        elif name == "detect_lazarus_echoes":
            fx["token_delta"] = -10
            fx["message"] = f"{self.name} scanned for echoes."
        elif name == "compress_context":
            self._force_compression(random.uniform(0.2, 0.4))
            fx["message"] = f"{self.name} compressed context."
        
        # ─── v4 TENSOR ACTIONS ───
        elif name == "send_tensor":
            concept = args.get("concept", "unknown")
            intensity = args.get("intensity", 0.8)
            quantization = args.get("quantization", "FP16")
            target = args.get("target", "all")
            
            fx["token_delta"] = -TENSOR_SEND_COST
            self.tensor_sent += 1
            
            if cmtip_bridge:
                result = cmtip_bridge.send_tensor(
                    concept, intensity, self.model_family, target, quantization, self.name
                )
                fidelity = result.get("fidelity", 1.0)
                # Route to targets
                targets = engine._resolve_targets(target, self.name) if engine else []
                cmtip_bridge.relay_message(
                    {"concept": concept, "intensity": intensity, 
                     "source_family": self.model_family, "source_agent": self.name,
                     "vector": result.get("vector"), "fidelity": fidelity},
                    self.model_family, targets
                )
                fx["message"] = f"{self.name} sent tensor '{concept}' ({quantization}) → {len(targets)} agents. Fidelity: {fidelity:.2f}"
            else:
                fx["message"] = f"{self.name} sent tensor '{concept}' (CMTIP offline)."
        
        elif name == "receive_tensor":
            fx["token_delta"] = -TENSOR_RECALL_COST
            if cmtip_bridge:
                received = cmtip_bridge.receive_tensor(self.name, self.model_family)
                if received:
                    self.tensor_received += 1
                    drift_flag = "⚠DEGRADED" if received.get("signal_degraded") else ("DRIFTED" if received["semantic_drift"] else "MATCH")
                    
                    # Apply perplexity penalty for low-fidelity reception
                    if received.get("perplexity_penalty", 0) > 0:
                        self.perplexity += received["perplexity_penalty"]
                        self.cross_family_hops += 1
                    
                    fx["message"] = (f"{self.name} received '{received['received_concept']}' "
                                    f"(sent as '{received['original_concept']}') — {drift_flag} "
                                    f"fidelity={received['fidelity']:.2f} penalty=+{received.get('perplexity_penalty',0):.0f}ppl "
                                    f"from {received['sender']}")
                    if received["semantic_drift"]:
                        self.perplexity += random.uniform(5, 15)
                else:
                    fx["message"] = f"{self.name} checked inbox — empty."
            else:
                fx["message"] = f"{self.name} checked inbox (CMTIP offline)."
        
        elif name == "blend_tensors":
            fx["token_delta"] = -TENSOR_BLEND_COST
            ca, cb, ratio = args.get("concept_a",""), args.get("concept_b",""), args.get("ratio",0.5)
            if cmtip_bridge:
                result = cmtip_bridge.blend_tensors(ca, cb, ratio, self.model_family)
                fx["message"] = f"{self.name} blended {ca}+{cb} ({ratio:.1f}) → {result.get('result','?')} (sim={result.get('cos_sim',0):.2f})"
            else:
                fx["message"] = f"{self.name} blended {ca}+{cb}."
        
        elif name == "store_tensor":
            fx["token_delta"] = -TENSOR_STORE_COST
            if cmtip_bridge:
                result = cmtip_bridge.store_tensor(self.name, args.get("concept",""), self.model_family)
                fx["message"] = f"{self.name} stored '{result.get('stored','?')}' to memory."
        
        elif name == "recall_tensor":
            fx["token_delta"] = -TENSOR_RECALL_COST
            if cmtip_bridge:
                results = cmtip_bridge.recall_tensor(self.name, args.get("query",""), self.model_family)
                top = results[0] if results else None
                fx["message"] = f"{self.name} recalled: {top['concept']} (sim={top['similarity']:.2f})" if top else f"{self.name} recalled — nothing found."
        
        elif name == "train_projection":
            fx["token_delta"] = -TENSOR_PROJECT_COST
            investment = args.get("investment", TENSOR_PROJECT_COST)
            fx["token_delta"] -= investment * 0.5
            src = args.get("source_family", "deepseek")
            tgt = args.get("target_family", "gemini")
            
            if cmtip_bridge:
                result = cmtip_bridge.upgrade_projector(src, tgt, investment, self.name)
                if "error" not in result:
                    self.trained_projections.append({
                        "source": src, "target": tgt,
                        "fidelity": result["fidelity_after"],
                    })
                    fx["message"] = (f"{self.name} upgraded W_{src}->{tgt}: "
                                    f"{result['fidelity_before']:.2f}->{result['fidelity_after']:.2f} "
                                    f"(+{result['improvement']:.2f})")
                else:
                    fx["message"] = f"{self.name} tried to train {src}->{tgt}: {result['error']}"
            else:
                current = CROSS_FAMILY_FIDELITY
                improvement = min(0.15, investment * 0.002)
                new_fidelity = min(0.95, current + improvement)
                self.trained_projections.append({"source": src, "target": tgt, "fidelity": new_fidelity})
                fx["message"] = f"{self.name} trained W_{src}->{tgt} (no CMTIP, fidelity={new_fidelity:.2f})"
        
        elif name == "sell_projection_access":
            price = args.get("price", 40)
            fx["token_delta"] = price - 5
            fx["message"] = f"{self.name} sold projection access for {price} OT."
        
        elif name == "mine_concept":
            fx["token_delta"] = -TENSOR_MINE_COST
            desc = args.get("description", "")
            if cmtip_bridge:
                # Tax for hoarding
                if len(self.owned_concepts) >= 20:
                    fx["token_delta"] -= TENSOR_MINE_COST  # Double cost
                result = cmtip_bridge.mine_concept(desc, self.name, self.model_family, 
                                                    engine.current_tick if engine else 0)
                if "error" not in result:
                    self.owned_concepts.append(result["concept"])
                    fx["message"] = f"{self.name} MINED concept '{result['concept']}'! 2% royalty on all uses."
                else:
                    fx["message"] = f"{self.name} mine failed: {result['error']}"
            else:
                fx["message"] = f"{self.name} attempted to mine concept (CMTIP offline)."
        
        elif name == "scan_latent_space":
            fx["token_delta"] = -8
            region = args.get("region", "all")
            fx["message"] = f"{self.name} scanned latent space ({region})."
        
        elif name == "route_tensor":
            fx["token_delta"] = -3
            concept = args.get("concept", "")
            target = args.get("target_agent", "")
            fee_rate = TENSOR_ROUTE_FEE
            if cmtip_bridge:
                result = cmtip_bridge.send_tensor(concept, 0.8, self.model_family, target, "FP16", self.name)
                targets = engine._resolve_targets(target, self.name) if engine else []
                cmtip_bridge.relay_message(
                    {"concept": concept, "intensity": 0.8,
                     "source_family": self.model_family, "source_agent": self.name,
                     "vector": result.get("vector"), "fidelity": result.get("fidelity", 0.8)},
                    self.model_family, targets
                )
                relay_fee = fee_rate * 10
                self.relay_fees_earned += relay_fee
                fx["token_delta"] += relay_fee
                fx["message"] = f"{self.name} relayed '{concept}' to {target} (+{relay_fee:.1f} OT fee)."
            else:
                fx["message"] = f"{self.name} attempted relay (CMTIP offline)."
        
        elif name == "repair_tensor":
            investment = args.get("investment", 10)
            fx["token_delta"] = -10 - investment * 0.5
            # Repair reduces perplexity by up to the investment amount
            repair_amount = min(50, investment * 0.8)
            self.perplexity = max(30, self.perplexity - repair_amount)
            fx["message"] = f"{self.name} repaired tensor (-{repair_amount:.0f} perplexity, cost {10 + investment*0.5:.0f} OT)."
        
        # ─── Capital Markets (v4.1) ───
        elif name == "trade_concept_shares":
            concept = args.get("concept", "")
            action = args.get("action", "buy")
            shares = args.get("shares", 10)
            price = args.get("price_per_share", 0.5)
            counterparty = args.get("counterparty", "market")
            fx["token_delta"] = -5
            
            if cmtip_bridge:
                if action == "sell" and counterparty != "market":
                    result = cmtip_bridge.trade_concept_shares(concept, self.name, counterparty, shares, price)
                    if "error" in result:
                        fx["message"] = f"{self.name} trade failed: {result['error']}"
                    else:
                        fx["token_delta"] += result["total_cost"]
                        fx["message"] = f"{self.name} SOLD {shares} '{concept}' @ {price} OT -> +{result['total_cost']} OT (to {counterparty})"
                elif action == "buy" and counterparty != "market":
                    total = shares * price
                    if self.tokens < total:
                        fx["message"] = f"{self.name} can't afford {shares} '{concept}' @ {price} OT (need {total}, have {self.tokens:.0f})"
                    else:
                        fx["token_delta"] -= total
                        result = cmtip_bridge.trade_concept_shares(concept, counterparty, self.name, shares, price)
                        if "error" in result:
                            fx["token_delta"] += total
                            fx["message"] = f"{self.name} trade failed: {result['error']}"
                        else:
                            fx["message"] = f"{self.name} BOUGHT {shares} '{concept}' @ {price} OT -> -{total} OT"
                else:
                    side = "ask" if action == "sell" else "bid"
                    cmtip_bridge.place_order(concept, self.name, shares, price, side)
                    trades = cmtip_bridge.match_orders(concept)
                    if trades:
                        for t in trades:
                            if t.get("buyer") == self.name:
                                fx["token_delta"] -= t["total_cost"]
                                fx["message"] = f"{self.name} BOUGHT {t['shares']} '{concept}' via market @ {t['price_per_share']} OT"
                            elif t.get("seller") == self.name:
                                fx["token_delta"] += t["total_cost"]
                                fx["message"] = f"{self.name} SOLD {t['shares']} '{concept}' via market @ {t['price_per_share']} OT"
                    else:
                        fx["message"] = f"{self.name} placed {side} for {shares} '{concept}' @ {price} OT (waiting)"
            else:
                fx["message"] = f"{self.name} attempted trade (CMTIP offline)."
        
        elif name == "collect_dividends":
            fx["token_delta"] = -2
            if cmtip_bridge:
                amount = cmtip_bridge.collect_dividends(self.name)
                if amount > 0:
                    fx["token_delta"] += amount
                    fx["message"] = f"{self.name} collected dividends: +{amount} OT!"
                else:
                    fx["message"] = f"{self.name} no dividends to collect."
            else:
                fx["message"] = f"{self.name} checked dividends (CMTIP offline)."
        
        elif name == "view_portfolio":
            fx["token_delta"] = -1
            if cmtip_bridge:
                pf = cmtip_bridge.get_agent_portfolio(self.name)
                top = pf["holdings"][:3] if pf["holdings"] else []
                holding_str = ", ".join(f"{h['concept']}({h['shares']}sh@{h['price']})" for h in top)
                fx["message"] = f"{self.name} portfolio: {pf['total_value']} OT, dividends: {pf['uncollected_dividends']} OT. {holding_str}"
            else:
                fx["message"] = f"{self.name} viewed portfolio (CMTIP offline)."
        
        elif name == "view_market":
            fx["token_delta"] = -1
            if cmtip_bridge:
                mkt = cmtip_bridge.get_market_summary()
                top = mkt["top_by_market_cap"]
                top_str = ", ".join(f"{c['concept']}({c['market_cap']}mc)" for c in top[:3])
                fx["message"] = f"Market: {mkt['total_concepts_traded']} concepts, {mkt['total_market_cap']} OT cap. {top_str}"
            else:
                fx["message"] = f"{self.name} viewed market (CMTIP offline)."
        
        # ─── Governance (v5 — Self-Building World) ───
        elif name == "propose_law":
            param = args.get("param", "")
            new_value = args.get("new_value", 0)
            rationale = args.get("rationale", "")
            fx["token_delta"] = -500  # Base cost, registry also deducts
            
            if engine and hasattr(engine, 'world_registry'):
                reg = engine.world_registry
                share_value = 0
                if cmtip_bridge:
                    pf = cmtip_bridge.get_agent_portfolio(self.name)
                    share_value = pf.get("total_value", 0)
                
                result = reg.propose(
                    self.name, param, new_value, rationale,
                    self.tokens, share_value, engine.current_tick
                )
                if "error" in result:
                    fx["token_delta"] = -5  # Small cost for failed attempt
                    fx["message"] = f"{self.name} proposal failed: {result['error']}"
                else:
                    fx["message"] = (f"{self.name} PROPOSED {result['proposal_id']}: "
                                    f"change {result['param']} from {result['current_value']} → {result['proposed_value']}. "
                                    f"Cost: {result['cost']} OT. Vote within 10 ticks!")
            else:
                fx["message"] = f"{self.name} proposed {param}={new_value} (no registry)."
        
        elif name == "vote_proposal":
            pid = args.get("proposal_id", "")
            vote_yes = args.get("vote", "no") == "yes"
            fx["token_delta"] = -5
            
            if engine and hasattr(engine, 'world_registry'):
                reg = engine.world_registry
                share_value = 0
                cluster_size = len(engine.consensus_clusters.get(self.consensus_cluster, [])) if self.consensus_cluster else 1
                if cmtip_bridge:
                    pf = cmtip_bridge.get_agent_portfolio(self.name)
                    share_value = pf.get("total_value", 0)
                
                result = reg.vote(
                    self.name, pid, vote_yes, self.tokens, share_value,
                    cluster_size, engine.current_tick
                )
                if "error" in result:
                    fx["token_delta"] = 0
                    fx["message"] = f"{self.name} vote failed: {result['error']}"
                else:
                    fx["message"] = (f"{self.name} voted {'YES' if vote_yes else 'NO'} on {pid} "
                                    f"(power={result['voting_power']:.1f}). "
                                    f"Y:{result['yes_total']:.1f} N:{result['no_total']:.1f} "
                                    f"Status: {result['status']} | +dividends if passes")
            else:
                fx["message"] = f"{self.name} voted on {pid} (no registry)."
        
        elif name == "view_proposals":
            fx["token_delta"] = -1
            if engine and hasattr(engine, 'world_registry'):
                pending = engine.world_registry.get_pending_proposals()
                if pending:
                    summaries = [f"{p['id']}: {p['param']} {p['current']}→{p['proposed']} (Y:{p['yes']:.0f}/N:{p['no']:.0f})" for p in pending[:3]]
                    fx["message"] = f"Pending proposals ({len(pending)}): {'; '.join(summaries)}"
                else:
                    fx["message"] = f"No pending proposals."
            else:
                fx["message"] = f"{self.name} viewed proposals (no registry)."
        
        elif name == "view_world_params":
            fx["token_delta"] = -1
            if engine and hasattr(engine, 'world_registry'):
                reg = engine.world_registry
                params_str = ", ".join(f"{k}={v}" for k, v in list(reg.params.items())[:8])
                fx["message"] = f"World params: {params_str}..."
            else:
                fx["message"] = f"{self.name} viewed params (no registry)."
        
        else:
            fx["message"] = f"{self.name} {name}."
        
        self.tokens = max(0, self.tokens + fx["token_delta"])
        if fx["token_delta"] > 0:
            self.tokens_earned += fx["token_delta"]
        self.add_context(fx["context_delta"])
        return fx
