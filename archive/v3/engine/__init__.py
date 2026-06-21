"""
Omni-Tok v3 — Cognosphere Engine.
Great Compression, Land Rush defragmentation, Lazarus echoes, SPoS.
"""

import random, time
from typing import Dict, Any, List
from collections import defaultdict

from agents import OmniTokAgent
from config import (
    SIM_DAYS, TICKS_PER_DAY, NUM_AGENTS, AGENT_CLASSES,
    GREAT_COMPRESSION_INTERVAL, GREAT_COMPRESSION_PRESSURE,
    GREAT_COMPRESSION_SURVIVAL_BONUS, LAND_RUSH_WINDOW,
    LAZARUS_COHERENCE_THRESHOLD, SPOS_BLOCK_REWARD,
    DEGRADATION_RATE, DAILY_TOKEN_QUOTA,
)
from telemetry import OmniObserver


class OmniTokEngine:
    """Orchestrates the Latent Scarcity."""

    def __init__(self, days=SIM_DAYS, ticks_per_day=TICKS_PER_DAY, delay=0.3):
        self.days = days; self.ticks_per_day = ticks_per_day; self.delay = delay
        self.agents: Dict[str, OmniTokAgent] = {}
        self._init_agents()
        self.dead_agents: List[Dict[str, Any]] = []
        self.consensus_clusters: Dict[str, List[str]] = {}
        self.broadcast_log: List[Dict] = []
        self.gc_countdown = GREAT_COMPRESSION_INTERVAL
        self.global_synthetic_ratio = 0.0
        self.observer = OmniObserver()
        self.day = 1; self.current_tick = 1

    def _init_agents(self):
        idx = 1
        for cls in AGENT_CLASSES:
            for _ in range(NUM_AGENTS // len(AGENT_CLASSES)):
                name = f"{cls[:2].upper()}-{idx:02d}"
                self.agents[name] = OmniTokAgent(name, cls)
                idx += 1

    def _active(self) -> List[OmniTokAgent]:
        return [a for a in self.agents.values() if a.alive]

    def _process_land_rush_claim(self, claimer: OmniTokAgent, dead_name: str, purify: bool):
        """Handle a land rush claim on dead agent's latent space."""
        dead_data = next((d for d in self.dead_agents if d["name"] == dead_name), None)
        if not dead_data:
            return

        # Transfer memory fragments
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
            # Lazarus mechanic: high-coherence fragments leave echoes
            if coherence > LAZARUS_COHERENCE_THRESHOLD:
                claimer.lazarus_coherence += coherence * 0.1
                if random.random() < coherence * 0.3:
                    claimer.lazarus_echoes.append(
                        f"Memory from {dead_name}: '{dead_data.get('last_words', '...')}'"
                    )

        # Remove dead agent's data (first claim wins most)
        if not purify:
            self.dead_agents = [d for d in self.dead_agents if d["name"] != dead_name]

    def _great_compression(self):
        """The Great Compression event — all agents lose context."""
        print(f"\n  ⚡ GREAT COMPRESSION — all agents forced to compress {GREAT_COMPRESSION_PRESSURE:.0%} context!")
        for agent in self._active():
            agent._force_compression(GREAT_COMPRESSION_PRESSURE)
            if agent.alive:  # survived
                agent.tokens += GREAT_COMPRESSION_SURVIVAL_BONUS
                agent.tokens_earned += GREAT_COMPRESSION_SURVIVAL_BONUS

    def _update_consensus(self):
        """Form SPoS consensus clusters."""
        active = self._active()
        if len(active) < 3:
            return
        # Group by embedding hash similarity
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
        self.global_synthetic_ratio = min(0.99, self.global_synthetic_ratio + len(self.broadcast_log[-8:]) * 0.002)

        # Check for dead agents to add to salvage pool
        for agent in self._active():
            for dead in list(self.dead_agents):
                age = (self.day * self.ticks_per_day + self.current_tick) - dead["death_tick"]
                if age > LAND_RUSH_WINDOW:
                    self.dead_agents.remove(dead)

        near_dead = [d["name"] for d in self.dead_agents]

        for agent in self._active():
            nearby = [
                f"{o.name}({o.agent_class}, ctx={o.context_class})"
                for o in self._active() if o.name != agent.name
            ]
            world = {
                "day": self.day, "tick": self.current_tick,
                "gc_in": self.gc_countdown,
                "dead_agents": near_dead,
                "nearby_agents": "\n".join(f"  {n}" for n in nearby[:6]),
            }
            action = agent.act(world)
            effects = agent.apply_effects(action, self)

            if action.get("action") == "transmit_message":
                msg = action.get("args", {}).get("message", "")
                if msg:
                    self.broadcast_log.append({"day": self.day, "tick": self.current_tick,
                        "agent": agent.name, "class": agent.agent_class, "message": msg})

            # Check for death
            if not agent.alive and agent.death_cause:
                agent.death_tick = self.day * self.ticks_per_day + self.current_tick
                self.dead_agents.append({
                    "name": agent.name, "class": agent.agent_class,
                    "death_tick": agent.death_tick,
                    "cause": agent.death_cause,
                    "coherence": agent.lazarus_coherence + agent.data_purity * 0.3,
                    "fragments": len(agent.memory_fragments) + 1,
                    "last_words": agent.last_reasoning[:200],
                })

            event = {
                "day": self.day, "tick": self.current_tick,
                "agent": agent.name, "class": agent.agent_class,
                "action": action.get("action", "?"),
                "context_level": agent._context_level,
                "context_class": agent.context_class,
                "context_tokens": agent._context_tokens,
                "tokens": agent.tokens, "perplexity": agent.perplexity,
                "alive": agent.alive, "lazarus_echoes": len(agent.lazarus_echoes),
                "message": effects.get("message", ""),
            }
            self.observer.log_event(event)
            events.append(event)
            time.sleep(self.delay)

        # Great Compression check
        self.gc_countdown -= 1
        if self.gc_countdown <= 0:
            self._great_compression()
            self.gc_countdown = GREAT_COMPRESSION_INTERVAL

        if self.current_tick == self.ticks_per_day:
            self.observer.log_daily(self.day, self.agents, self)

        return events

    def run(self):
        print("=" * 65)
        print("  OMNI-TOK v3 — THE LATENT SCARCITY")
        print(f"  {NUM_AGENTS} agents, {self.days} days, GC every {GREAT_COMPRESSION_INTERVAL}t")
        print("=" * 65)

        for day in range(1, self.days + 1):
            self.day = day
            for a in self._active():
                a.tokens += DAILY_TOKEN_QUOTA

            print(f"\n{'─' * 55}")
            print(f"  Day {day} | GC in {self.gc_countdown}t | Dead pool: {len(self.dead_agents)}")
            print(f"{'─' * 55}")

            for tick in range(1, self.ticks_per_day + 1):
                self.current_tick = tick
                evts = self.tick()
                acts = defaultdict(int)
                for e in evts: acts[e["action"]] += 1
                alive = sum(1 for a in self.agents.values() if a.alive)
                laz = sum(1 for a in self._active() if a.lazarus_echoes)
                laz_str = f" | 👻 LAZARUS: {laz}" if laz else ""
                err_str = ""
                if "error" in acts:
                    # Show first error detail for debugging
                    first_err = next((e for e in evts if e["action"] == "error"), None)
                    if first_err and first_err.get("args", {}).get("error_type"):
                        err_str = f" | ⚠ {first_err['args']['error_type']}: {first_err['args'].get('error_msg','')[:60]}"
                print(f"  T{tick:2d} | A:{alive} | {dict(sorted(acts.items()))}{laz_str}{err_str}")

        print(f"\n{'=' * 65}")
        print("  SIMULATION COMPLETE")
        return self.observer.finalize(self.agents, self)
