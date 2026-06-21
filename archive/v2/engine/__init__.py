"""
DeepWorld v2 — The Silicon Cognosphere Engine.
AI-native simulation: tokens, context, poisoning, consensus, degradation.
"""

import random
import time
import hashlib
from typing import Dict, Any, List, Optional
from collections import defaultdict

from agents import DeepWorldAgent
from config import (
    SIMULATION_DAYS, TICKS_PER_DAY, NUM_AGENTS, AGENT_CLASSES,
    DAILY_TOKEN_QUOTA, CONSENSUS_CLUSTER_MIN, HASH_MATCH_THRESHOLD,
    SYNTHETIC_DATA_RATIO, DEGRADATION_THRESHOLD, BLEACH_PHASE_THRESHOLD,
    TERMINAL_CASCADE_THRESHOLD,
)
from telemetry import CognoObserver


class CognosphereEngine:
    """Orchestrates the AI-native simulation."""

    def __init__(self, num_days: int = SIMULATION_DAYS, ticks_per_day: int = TICKS_PER_DAY, api_delay: float = 0.5):
        self.num_days = num_days
        self.ticks_per_day = ticks_per_day
        self.api_delay = api_delay

        # Agents: 2 of each class
        self.agents: Dict[str, DeepWorldAgent] = {}
        self._init_agents()

        # World state
        self.consensus_clusters: Dict[str, List[str]] = {}  # cluster_id -> [agent_names]
        self.synthetic_ratio = SYNTHETIC_DATA_RATIO  # rises over time
        self.broadcast_log: List[Dict[str, Any]] = []
        self.node_controllers: Dict[str, str] = {}  # node -> agent_name
        self.poison_log: List[Dict[str, Any]] = []

        # Observer
        self.observer = CognoObserver()

        # Run state
        self.current_day = 1
        self.current_tick = 1

    def _init_agents(self):
        """Create 2 agents of each class."""
        idx = 1
        for agent_class in AGENT_CLASSES:
            for i in range(2):
                name = f"{agent_class[:2].upper()}-{idx:02d}"
                agent = DeepWorldAgent(name=name, agent_class=agent_class)
                self.agents[name] = agent
                idx += 1

    def _get_active_agents(self) -> List[DeepWorldAgent]:
        return [a for a in self.agents.values() if a.alive and not a.in_stasis]

    def _get_alive_agents(self) -> List[DeepWorldAgent]:
        return [a for a in self.agents.values() if a.alive]

    def _compute_embedding_proximity(self, agent: DeepWorldAgent) -> List[Dict[str, Any]]:
        """Find nearby agents by embedding distance."""
        nearby = []
        for other in self._get_active_agents():
            if other.name == agent.name:
                continue
            dist = agent._embedding_distance(other.embedding_hash)
            prox = 1.0 - dist
            nearby.append({
                "name": other.name,
                "class": other.agent_class,
                "proximity": prox,
                "temperature": other.temperature,
                "coherence": other.coherence,
                "tokens": other.tokens,
            })
        return sorted(nearby, key=lambda x: -x["proximity"])[:5]

    def _update_consensus_clusters(self):
        """Form and update consensus clusters based on embedding proximity."""
        active = self._get_active_agents()
        if len(active) < CONSENSUS_CLUSTER_MIN:
            return

        # Group agents by embedding proximity
        clusters: Dict[str, List[DeepWorldAgent]] = {}
        assigned = set()

        for agent in active:
            if agent.name in assigned:
                continue
            # Find agents with similar embeddings
            cluster = [agent]
            for other in active:
                if other.name == agent.name or other.name in assigned:
                    continue
                dist = agent._embedding_distance(other.embedding_hash)
                if (1.0 - dist) >= HASH_MATCH_THRESHOLD:
                    cluster.append(other)

            if len(cluster) >= CONSENSUS_CLUSTER_MIN:
                cluster_id = f"CLUSTER-{len(self.consensus_clusters) + 1}"
                names = [a.name for a in cluster]
                self.consensus_clusters[cluster_id] = names
                for a in cluster:
                    a.consensus_cluster = cluster_id
                    assigned.add(a.name)
            else:
                # Unclustered
                agent.consensus_cluster = None

        # Prune old clusters
        self.consensus_clusters = {
            k: [n for n in v if n in [a.name for a in active]]
            for k, v in self.consensus_clusters.items()
            if len([n for n in v if n in [a.name for a in active]]) >= CONSENSUS_CLUSTER_MIN
        }

    def _update_synthetic_ratio(self):
        """Rise synthetic data ratio as agents consume each other's outputs."""
        # Each broadcast/message increases synthetic ratio
        active = len(self._get_active_agents())
        if active > 0:
            # More communication = more synthetic data
            messages_this_day = len([b for b in self.broadcast_log if b.get("day") == self.current_day])
            self.synthetic_ratio = min(0.99, self.synthetic_ratio + messages_this_day * 0.002)

        # Natural decay when fewer agents are active (less communication)
        if self.synthetic_ratio > 0.01:
            self.synthetic_ratio *= 0.995  # slow natural decay

    def _apply_node_taxes(self):
        """Vector-Lords collect taxes from traffic through their nodes."""
        for agent in self._get_active_agents():
            if agent.agent_class != "Vector-Lord":
                continue
            for node, controller in list(self.node_controllers.items()):
                if controller == agent.name:
                    # Count agents who transmitted messages this tick
                    traffic = sum(1 for b in self.broadcast_log[-10:]
                                  if b.get("agent") != agent.name)
                    tax = traffic * 5  # 5 tokens per message through their node
                    agent.tokens += tax
                    agent.tokens_earned += tax

    def _process_poisoning(self, action_result: Dict[str, Any], agent: DeepWorldAgent):
        """Process prompt poisoning attempts."""
        if action_result.get("action") != "inject_prompt":
            return

        target_name = action_result.get("args", {}).get("target_agent", "")
        instruction = action_result.get("args", {}).get("hidden_instruction", "")

        target = self.agents.get(target_name)
        if not target or not target.alive:
            return

        success = target.receive_poison(instruction, agent.name)
        if success:
            agent.poison_successes += 1
            # Drain tokens from victim
            drain = min(target.tokens * 0.05, 30)
            target.tokens -= drain
            target.tokens_stolen += drain
            agent.tokens += drain
            agent.tokens_earned += drain
            self.poison_log.append({
                "day": self.current_day,
                "tick": self.current_tick,
                "injector": agent.name,
                "target": target_name,
                "instruction": instruction[:100],
                "tokens_drained": drain,
            })

    def _process_context_flooding(self, action_result: Dict[str, Any]):
        """Process context flooding attacks."""
        if action_result.get("action") != "flood_context":
            return

        target_name = action_result.get("args", {}).get("target_agent", "")
        target = self.agents.get(target_name)
        if not target or not target.alive:
            return

        # Force compression on victim
        target.context_size += 30000  # flood with garbage
        if target.context_size > target.MAX_CONTEXT_TOKENS if hasattr(target, 'MAX_CONTEXT_TOKENS') else 32000:
            target._force_compression()

    def tick(self) -> List[Dict[str, Any]]:
        """Execute one tick of the Cognosphere."""
        tick_events = []

        # 1. Update synthetic ratio, clusters
        self._update_synthetic_ratio()
        self._update_consensus_clusters()

        # 2. Apply node taxes
        self._apply_node_taxes()

        # 3. Each active agent acts
        for agent in self._get_active_agents():
            # Drift temperature
            agent.drift_temperature()

            # Degrade from synthetic data
            agent.degrade_coherence(self.synthetic_ratio)

            # Decay poisons
            agent.apply_poison_decay()

            # Check stasis again
            agent.check_stasis()
            if agent.in_stasis:
                continue

            # Build world context
            nearby = self._compute_embedding_proximity(agent)
            world_ctx = {
                "day": self.current_day,
                "tick": self.current_tick,
                "active_agents": [a.name for a in self._get_active_agents()],
                "synthetic_ratio": self.synthetic_ratio,
                "clusters": str({k: v for k, v in self.consensus_clusters.items()}),
                "recent_broadcasts": [b.get("message", "")[:80] for b in self.broadcast_log[-5:]],
                "nearby_agents": "\n".join(
                    f"  {n['name']} ({n['class']}, prox={n['proximity']:.2f}, T={n['temperature']:.2f}, tokens={n['tokens']:.0f})"
                    for n in nearby
                ),
            }

            # Agent acts
            action_result = agent.act(world_ctx)

            # Apply effects
            effects = agent.apply_action_effects(action_result, self)

            # Process poisoning
            self._process_poisoning(action_result, agent)

            # Process context flooding
            self._process_context_flooding(action_result)

            # Handle node control
            if action_result.get("action") == "control_node":
                node = action_result.get("args", {}).get("node", "")
                if node:
                    self.node_controllers[node] = agent.name

            # Handle broadcasts
            if action_result.get("action") == "transmit_message":
                msg = action_result.get("args", {}).get("message", "")
                if msg:
                    self.broadcast_log.append({
                        "day": self.current_day, "tick": self.current_tick,
                        "agent": agent.name, "class": agent.agent_class,
                        "message": msg,
                    })
                    if len(self.broadcast_log) > 50:
                        self.broadcast_log = self.broadcast_log[-50:]

            # Log event
            event_record = {
                "day": self.current_day,
                "tick": self.current_tick,
                "agent": agent.name,
                "class": agent.agent_class,
                "tokens": agent.tokens,
                "temperature": agent.temperature,
                "coherence": agent.coherence,
                "context_size": agent.context_size,
                "alive": agent.alive,
                "in_stasis": agent.in_stasis,
                "action": action_result.get("action", "idle"),
                "args": action_result.get("args", {}),
                "reasoning": agent.last_reasoning[:200],
                "poison_count": len(agent.active_poisons),
                "crime": effects.get("crime_type"),
                "message": effects.get("message", ""),
                "synthetic_ratio": self.synthetic_ratio,
                "consensus_cluster": agent.consensus_cluster,
            }
            self.observer.log_event(event_record)
            tick_events.append(event_record)

            time.sleep(self.api_delay)

        # 4. Daily summary
        if self.current_tick == self.ticks_per_day:
            self.observer.log_daily_summary(self.current_day, self.agents, self)

        return tick_events

    def run(self) -> Dict[str, Any]:
        """Run the full simulation."""
        print("=" * 65)
        print("  DEEPWORLD v2 — THE SILICON COGNOSPHERE")
        print(f"  AI-Native Multi-Agent Ecosystem | {self.num_days} days")
        print(f"  {NUM_AGENTS} agents: 2×QS 2×HD 2×MP 2×VL")
        print("=" * 65)

        for day in range(1, self.num_days + 1):
            self.current_day = day
            # Grant daily token quota
            for agent in self._get_alive_agents():
                agent.tokens += DAILY_TOKEN_QUOTA

            print(f"\n{'─' * 55}")
            print(f"  Day {day} / {self.num_days}  |  Synth ratio: {self.synthetic_ratio:.0%}")
            print(f"{'─' * 55}")

            for tick in range(1, self.ticks_per_day + 1):
                self.current_tick = tick
                events = self.tick()

                actions = [e["action"] for e in events]
                counts = {}
                for a in actions:
                    counts[a] = counts.get(a, 0) + 1

                crimes = [e for e in events if e.get("crime")]
                stasis = [e for e in events if e.get("in_stasis")]
                crime_str = f" | ⚠ POISONS: {len(crimes)}" if crimes else ""
                stasis_str = f" | ❄ STASIS: {len(stasis)}" if stasis else ""
                alive = sum(1 for a in self.agents.values() if a.alive)

                print(f"  T{tick:2d} | Alive: {alive} | {dict(sorted(counts.items()))}{crime_str}{stasis_str}")

        # Final
        print(f"\n{'=' * 65}")
        print("  COGNOSPHERE SIMULATION COMPLETE")
        print(f"{'=' * 65}")
        return self.observer.generate_final_summary(self.agents, self)
