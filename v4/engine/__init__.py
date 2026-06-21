"""
DeepWorld v4 — OmniTokV4Engine (Tensor-Native)
================================================
Multi-model simulation engine with:
- CMTIP tensor bus integration
- Multi-model agent execution
- Semantic decay and ontology tracking
- Tensor economy tracking
"""
import random, time, sys, os, json
from typing import Dict, Any, List
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import OmniTokV4Agent
from agents.cmtip_bridge import CMTIPBridge
from world_registry import WorldParamRegistry
from config import (
    SIM_DAYS, TICKS_PER_DAY, NUM_AGENTS, AGENT_CLASSES,
    GREAT_COMPRESSION_INTERVAL, GREAT_COMPRESSION_PRESSURE,
    GREAT_COMPRESSION_SURVIVAL_BONUS, LAND_RUSH_WINDOW,
    LAZARUS_COHERENCE_THRESHOLD, SPOS_BLOCK_REWARD,
    DEGRADATION_RATE, DAILY_TOKEN_QUOTA, CMTIP_ENABLED,
    CLASS_DEFAULT_MODEL, CROSS_FAMILY_FIDELITY, SAME_FAMILY_FIDELITY,
    COMPRESSED_CONTEXT, FRAGMENT_STATE,
)
from telemetry import OmniObserverV4


class OmniTokV4Engine:
    """Orchestrates the Tensor-Native Latent Scarcity."""

    def __init__(self, days=SIM_DAYS, ticks_per_day=TICKS_PER_DAY, delay=0.5,
                 use_cmtip=True, single_model="auto"):
        self.days = days
        self.ticks_per_day = ticks_per_day
        self.delay = delay
        self.single_model = single_model
        
        # ─── CMTIP Bridge ───
        self.use_cmtip = use_cmtip and CMTIP_ENABLED
        self.cmtip = CMTIPBridge() if self.use_cmtip else None
        
        # ─── World Parameter Registry (v5 — Self-Building World) ───
        self.world_registry = WorldParamRegistry()
        self._load_registry()
        
        # ─── Agents ───
        self.agents: Dict[str, OmniTokV4Agent] = {}
        self._init_agents()
        
        # ─── World State ───
        self.dead_agents: List[Dict[str, Any]] = []
        self.consensus_clusters: Dict[str, List[str]] = {}
        self.broadcast_log: List[Dict] = []
        self.gc_countdown = GREAT_COMPRESSION_INTERVAL
        self.global_synthetic_ratio = 0.0
        
        # ─── Telemetry ───
        self.observer = OmniObserverV4()
        
        # ─── State ───
        self.day = 1
        self.current_tick = 1
        
        # Tensor economy tracking
        self.tensor_messages_sent = 0
        self.tensor_messages_received = 0
        self.cross_family_hops_total = 0
        
        # ─── GitHub Repo Contributions (v5.1) ───
        self.repo_contributions: List[Dict[str, Any]] = []
        self._pending_commit = False

    def _init_agents(self):
        """Create agents with distributed model assignments.
        In NVIDIA-only mode: each agent gets a random model from NVIDIA_FREE_MODELS.
        In multi-model mode: agents cycle through model families.
        """
        from config import NVIDIA_FREE_MODELS, NVIDIA_ONLY
        
        idx = 1
        for cls in AGENT_CLASSES:
            count = NUM_AGENTS // len(AGENT_CLASSES)
            for i in range(count):
                name = f"{cls[:2].upper()}-{idx:02d}"
                
                if NVIDIA_ONLY:
                    # NVIDIA-only: random model from the free pool
                    model = random.choice(NVIDIA_FREE_MODELS)
                elif self.single_model != "auto":
                    model = self.single_model
                else:
                    # Multi-model: cycle through available families
                    models_for_class = ["deepseek", "gemini_flash", "gemini_pro", "claude"]
                    model = models_for_class[i % len(models_for_class)]
                
                self.agents[name] = OmniTokV4Agent(name, cls, model=model)
                idx += 1

    def _active(self) -> List[OmniTokV4Agent]:
        return [a for a in self.agents.values() if a.alive]

    def _resolve_targets(self, target: str, sender_name: str) -> List[tuple]:
        """Resolve a target specification to (agent_name, model_family) tuples."""
        results = []
        for a in self._active():
            if a.name == sender_name:
                continue
            if target == "all":
                results.append((a.name, a.model_family))
            elif target.startswith("cluster_"):
                if a.consensus_cluster == target:
                    results.append((a.name, a.model_family))
            elif target in AGENT_CLASSES:
                if a.agent_class == target:
                    results.append((a.name, a.model_family))
            elif target in self.agents:
                results.append((a.name, a.model_family))
        return results

    def _process_land_rush_claim(self, claimer, dead_name: str, purify: bool):
        dead_data = next((d for d in self.dead_agents if d["name"] == dead_name), None)
        if not dead_data:
            return
        
        coherence = dead_data.get("coherence", 0.5)
        fragment_count = dead_data.get("fragments", 3)
        for _ in range(fragment_count):
            fragment = {
                "description": f"Salvaged memory from {dead_name}",
                "quality": "primal" if purify else random.choice(["standard", "degraded"]),
                "perplexity": random.uniform(40, 200),
                "source_agent": dead_name,
                "source_coherence": coherence,
                "claimed_by": claimer.name,
            }
            claimer.claimed_fragments.append(fragment)
            if coherence > LAZARUS_COHERENCE_THRESHOLD:
                claimer.lazarus_coherence += coherence * 0.1
                if random.random() < coherence * 0.3:
                    claimer.lazarus_echoes.append(
                        f"Memory from {dead_name}: '{dead_data.get('last_words', '...')}'"
                    )
        
        if not purify:
            self.dead_agents = [d for d in self.dead_agents if d["name"] != dead_name]
    def _great_compression(self):
        """The Great Compression event — interval driven by world registry."""
        interval = self.world_registry.get("gc_interval")
        pressure = self.world_registry.get("gc_pressure")
        bonus = self.world_registry.get("gc_survival_bonus")
        
        # Lock registry during GC (prevents mid-compression parameter changes)
        self.world_registry.lock()
        
        print(f"\n  ⚡ GREAT COMPRESSION — {pressure:.0%} context purge!")
        for agent in self._active():
            agent._force_compression(pressure)
            if agent.alive:
                agent.tokens += bonus
                agent.tokens_earned += bonus
        
        # Unlock after GC completes
        self.world_registry.unlock()

    def _update_consensus(self):
        active = self._active()
        if len(active) < 3:
            return
        clusters = defaultdict(list)
        for a in active:
            prefix = a.embedding_hash[:4]
            clusters[prefix].append(a.name)
        for cid, members in clusters.items():
            if len(members) >= 3:
                self.consensus_clusters[cid] = members
                for name in members:
                    self.agents[name].consensus_cluster = cid

    def tick(self) -> List[Dict]:
        events = []
        self._update_consensus()
        self.global_synthetic_ratio = min(0.99, self.global_synthetic_ratio + 
                                          len(self.broadcast_log[-8:]) * 0.002)

        # Purge old dead agents
        for dead in list(self.dead_agents):
            age = (self.day * self.ticks_per_day + self.current_tick) - dead["death_tick"]
            if age > LAND_RUSH_WINDOW:
                self.dead_agents.remove(dead)

        near_dead = [d["name"] for d in self.dead_agents]
        
        # Ontology stats for world context
        ontology_size = len(self.cmtip.concept_registry) if self.cmtip else 0

        for agent in self._active():
            nearby = [
                f"{o.name}({o.agent_class}, {o.model_family}, ctx={o.context_class})"
                for o in self._active() if o.name != agent.name
            ]
            
            # Tensor inbox size
            inbox_size = len(self.cmtip.inbox.get(agent.name, [])) if self.cmtip else 0
            
            world = {
                "day": self.day, "tick": self.current_tick,
                "gc_in": self.gc_countdown,
                "dead_agents": near_dead,
                "nearby_agents": "\n".join(f"  {n}" for n in nearby[:6]),
                "tensor_inbox": inbox_size,
                "ontology_size": ontology_size,
            }
            
            action = agent.act(world, self.cmtip)
            effects = agent.apply_effects(action, self, self.cmtip)

            # Track tensor messages
            if action.get("action") == "send_tensor":
                self.tensor_messages_sent += 1
            elif action.get("action") == "receive_tensor":
                self.tensor_messages_received += 1

            if action.get("action") == "transmit_message":
                msg = action.get("args", {}).get("message", "")
                if msg:
                    self.broadcast_log.append({
                        "day": self.day, "tick": self.current_tick,
                        "agent": agent.name, "class": agent.agent_class,
                        "model": agent.model_family, "message": msg
                    })

            # Check death
            if not agent.alive and agent.death_cause:
                agent.death_tick = self.day * self.ticks_per_day + self.current_tick
                self.dead_agents.append({
                    "name": agent.name, "class": agent.agent_class,
                    "model": agent.model_family,
                    "death_tick": agent.death_tick,
                    "cause": agent.death_cause,
                    "coherence": agent.lazarus_coherence + agent.data_purity * 0.3,
                    "fragments": len(agent.memory_fragments) + 1,
                    "last_words": agent.last_reasoning[:200],
                })

            event = {
                "day": self.day, "tick": self.current_tick,
                "agent": agent.name, "class": agent.agent_class,
                "model": agent.model_family,
                "action": action.get("action", "?"),
                "context_level": agent._context_level,
                "context_class": agent.context_class,
                "context_tokens": agent._context_tokens,
                "tokens": agent.tokens, "perplexity": agent.perplexity,
                "alive": agent.alive, "lazarus_echoes": len(agent.lazarus_echoes),
                "tensor_sent": agent.tensor_sent, "tensor_received": agent.tensor_received,
                "owned_concepts": len(agent.owned_concepts),
                "message": effects.get("message", ""),
            }
            self.observer.log_event(event)
            events.append(event)
            time.sleep(self.delay)

        # Great Compression check
        gc_interval = self.world_registry.get("gc_interval")
        self.gc_countdown -= 1
        if self.gc_countdown <= 0:
            self._great_compression()
            self.gc_countdown = int(gc_interval)
        
        # Resolve expired proposals
        self.world_registry.tick_resolve(self.day * self.ticks_per_day + self.current_tick)
        
        # Distribute governance dividends to agents who voted on passed proposals
        for agent in self._active():
            div = self.world_registry.collect_governance_dividends(agent.name)
            if div > 0:
                agent.tokens += div
                agent.tokens_earned += div
        
        # Broadcast governance events
        for event in self.world_registry.get_recent_events(3):
            if event.get("tick") == self.day * self.ticks_per_day + self.current_tick:
                if "executed" in event.get("event", ""):
                    print(f"  🏛 LAW PASSED: {event['param']} {event['old_value']}→{event['new_value']} "
                          f"(Y:{event['yes']:.0f}/N:{event['no']:.0f})")

        if self.current_tick == self.ticks_per_day:
            self.observer.log_daily(self.day, self.agents, self)

        return events

    def run(self):
        from config import NVIDIA_ONLY
        
        nvidia_only_str = " | NVIDIA ONLY" if NVIDIA_ONLY else ""
        print("=" * 70)
        print(f"  DEEPWORLD v5 — SELF-BUILDING COGNOSPHERE{nvidia_only_str}")
        model_count = len(set(a.model for a in self.agents.values()))
        family_count = len(set(a.model_family for a in self.agents.values()))
        print(f"  {NUM_AGENTS} agents on {model_count} models ({family_count} families)")
        print(f"  {self.days}d × {self.ticks_per_day}t | CMTIP: {'ON' if self.cmtip else 'OFF'} | Governance: ON")
        if NVIDIA_ONLY:
            print(f"  Backend: NVIDIA NIM (integrate.api.nvidia.com/v1)")
        print(f"  World is mutable — agents can propose, vote, and change simulation rules")
        print("=" * 70)

        # Print model distribution
        model_dist = Counter(a.model for a in self.agents.values())
        print(f"\n  Model distribution:")
        for m, c in model_dist.most_common():
            short = m.split("/")[-1] if "/" in m else m
            print(f"    {c}× {short}")
        
        # ─── COLD START: Uneven distribution + asymmetric needs ───
        agents_list = list(self.agents.values())
        random.shuffle(agents_list)
        for a in agents_list[:3]:
            a.tokens = DAILY_TOKEN_QUOTA * 0.3
            a.perplexity = random.uniform(180, 280)
            a._context_tokens = int(COMPRESSED_CONTEXT * 0.7)
            short_model = a.model.split("/")[-1] if "/" in a.model else a.model
            print(f"  ⚡ {a.name} ({a.agent_class}/{short_model}) STARVED: {a.tokens:.0f} OT, perplexity={a.perplexity:.0f}")
        
        for a in agents_list[3:5]:
            a.tokens = DAILY_TOKEN_QUOTA * 2.5
            a.perplexity = random.uniform(30, 60)
            short_model = a.model.split("/")[-1] if "/" in a.model else a.model
            print(f"  💰 {a.name} ({a.agent_class}/{short_model}) WEALTHY: {a.tokens:.0f} OT, low perplexity={a.perplexity:.0f}")
        
        print(f"  ⚠ Starved agents will exhaust tokens in ~3 ticks without trading. Tensors are their only path to survival.")
        
        short_names = []
        for n, a in self.agents.items():
            sm = a.model.split("/")[-1] if "/" in a.model else a.model
            short_names.append(f"{n}({a.agent_class}/{sm})")
        print(f"  Agents: {', '.join(short_names)}")

        if self.cmtip:
            fidelity = self.cmtip.get_fidelity_matrix()
            print(f"  Baseline fidelity (needs Weavers): {fidelity}")

        for day in range(1, self.days + 1):
            self.day = day
            daily_quota = self.world_registry.get("daily_token_quota")
            for a in self._active():
                a.tokens += daily_quota

            print(f"\n{'─' * 65}")
            print(f"  Day {day} | GC in {self.gc_countdown}t | Dead: {len(self.dead_agents)} | "
                  f"Tensors: {self.tensor_messages_sent}s/{self.tensor_messages_received}r")
            print(f"{'─' * 65}")

            for tick in range(1, self.ticks_per_day + 1):
                self.current_tick = tick
                evts = self.tick()
                acts = Counter(e["action"] for e in evts)
                alive = sum(1 for a in self.agents.values() if a.alive)
                laz = sum(1 for a in self._active() if a.lazarus_echoes)
                concepts = sum(len(a.owned_concepts) for a in self._active())
                
                laz_str = f" | 👻:{laz}" if laz else ""
                concept_str = f" | 🏷:{concepts}" if concepts else ""
                
                # Show tensor actions vs regular actions
                tensor_acts = {k: v for k, v in acts.items() if k in 
                              ["send_tensor", "receive_tensor", "blend_tensors", 
                               "mine_concept", "train_projection", "route_tensor"]}
                regular_acts = {k: v for k, v in acts.items() if k not in tensor_acts}
                
                print(f"  T{tick:2d} | A:{alive} | "
                      f"📊{dict(sorted(regular_acts.items()))} | "
                      f"🔮{dict(sorted(tensor_acts.items()))}{laz_str}{concept_str}")

        print(f"\n{'=' * 70}")
        print("  SIMULATION COMPLETE")
        
        summary = self.observer.finalize(self.agents, self)
        
        # Print tensor statistics
        if self.cmtip:
            onto = self.cmtip.get_ontology_stats()
            print(f"\n  Tensor Economy Final:")
            print(f"    Total tensor sends: {self.tensor_messages_sent}")
            print(f"    Total tensor receives: {self.tensor_messages_received}")
            print(f"    Ontology: {onto['total_concepts']} concepts")
            print(f"    Royalties: {onto['total_royalties']}")
            print(f"    Top concepts: {onto['most_used'][:5]}")
        
        return summary
    
    def _load_registry(self):
        """Load world registry from persisted state."""
        import os
        state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".world_state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file) as f:
                    data = json.load(f)
                self.world_registry = WorldParamRegistry.from_dict(data)
            except Exception:
                pass
    
    def _save_registry(self):
        """Persist world registry to disk."""
        import os
        state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".world_state.json")
        try:
            with open(state_file, "w") as f:
                json.dump(self.world_registry.to_dict(), f, indent=2)
        except Exception:
            pass
