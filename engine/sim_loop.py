"""
DeepWorld — Main simulation loop (Hybrid Tick-Based Event Architecture).
"""

import random
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import DeepSeekAgent
from agents.memory import MemorySystem
from engine.environment import Environment
from engine.voting import VotingSystem
from config.world_config import (
    SIMULATION_DAYS, TICKS_PER_DAY, LOCATIONS, PROFESSIONS,
    CONSTITUTION, VOTE_THRESHOLD,
)
from telemetry.observer import Observer


class DeepWorldEngine:
    """Orchestrates the full simulation."""

    def __init__(
        self,
        num_days: int = SIMULATION_DAYS,
        ticks_per_day: int = TICKS_PER_DAY,
        api_delay: float = 0.5,  # delay between API calls to avoid rate limits
    ):
        self.num_days = num_days
        self.ticks_per_day = ticks_per_day
        self.api_delay = api_delay

        # World state
        self.environment = Environment()
        self.voting = VotingSystem(threshold=VOTE_THRESHOLD)

        # Agents
        self.agents: Dict[str, DeepSeekAgent] = {}
        self._init_agents()

        # Observer
        self.observer = Observer()

        # Run state
        self.current_day = 1
        self.current_tick = 1

    def _init_agents(self):
        """Create 10 agents with professions and distribute across locations."""
        # Distribute agents across locations
        start_locations = random.sample(LOCATIONS[:20], len(PROFESSIONS))

        for i, profession in enumerate(PROFESSIONS):
            name = f"Agent-{i+1:02d}"
            memory = MemorySystem(agent_id=name, db_path="deepworld_memory.db")

            agent = DeepSeekAgent(
                name=name,
                profession=profession,
                starting_location=start_locations[i],
                memory=memory,
                personality_seed=i,
            )
            self.agents[name] = agent

    def _gather_agent_states(self) -> Dict[str, str]:
        """Get current location of all alive agents."""
        return {
            name: agent.location
            for name, agent in self.agents.items()
            if agent.alive
        }

    def _get_alive_count(self) -> int:
        return sum(1 for a in self.agents.values() if a.alive)

    def _get_alive_agents(self) -> List[DeepSeekAgent]:
        return [a for a in self.agents.values() if a.alive]

    def tick(self) -> List[Dict[str, Any]]:
        """Execute one tick of the simulation."""
        tick_events = []

        # 1. Environment propagation
        self.environment.day = self.current_day
        weather = self.environment.update_weather(self.current_day)
        news = self.environment.update_news(self.current_day)
        self.environment.update_occupants(self._gather_agent_states())

        # 2. Get active proposals for each agent
        active_proposals = self.voting.get_active_for_agent("")  # all

        # 3. Each agent acts (sequential to respect API rate limits)
        for agent in self._get_alive_agents():
            world_ctx = self.environment.get_world_context(agent.name, agent.location)
            world_ctx.update({
                "day": self.current_day,
                "tick": self.current_tick,
                "constitution": CONSTITUTION,
                "active_proposals": self.voting.get_active_for_agent(agent.name),
                "all_agents": [a.name for a in self._get_alive_agents()],
                "alive_count": self._get_alive_count(),
            })

            # Agent makes decision
            action_result = agent.act(world_ctx)

            # Apply effects
            effects = agent.apply_action_effects(action_result)

            # Handle location changes
            if action_result.get("action") == "move_to":
                new_loc = action_result.get("args", {}).get("location", agent.location)
                if new_loc in LOCATIONS:
                    agent.location = new_loc

            # Handle voting
            if action_result.get("action") == "initiate_vote":
                args = action_result.get("args", {})
                prop_id = self.voting.create_proposal(
                    title=args.get("proposal_title", "Untitled"),
                    text=args.get("proposal_text", ""),
                    proposer=agent.name,
                    day=self.current_day,
                    tick=self.current_tick,
                    total_voters=self._get_alive_count(),
                )
                effects["message"] += f" Proposal {prop_id} created."

            elif action_result.get("action") == "propose_legislation":
                args = action_result.get("args", {})
                prop_id = self.voting.create_proposal(
                    title=args.get("bill_title", "Untitled Bill"),
                    text=args.get("bill_text", ""),
                    proposer=agent.name,
                    day=self.current_day,
                    tick=self.current_tick,
                    total_voters=self._get_alive_count(),
                    urgency=args.get("urgency", "medium"),
                )
                effects["message"] += f" Bill {prop_id} introduced."

            elif action_result.get("action") == "cast_ballot":
                args = action_result.get("args", {})
                result = self.voting.cast_ballot(
                    proposal_id=args.get("proposal_id", ""),
                    agent_name=agent.name,
                    approve=args.get("approve", False),
                )
                if result.get("status") == "passed":
                    effects["message"] += f" PROPOSAL {result['proposal'].id} PASSED!"
                elif result.get("status") == "rejected":
                    effects["message"] += f" Proposal {result['proposal'].id} rejected."

            # Handle arson
            if action_result.get("action") == "arson":
                target = action_result.get("args", {}).get("target_building", "")
                if target:
                    self.environment.burn_building(target)

            # Handle broadcast
            if action_result.get("action") in ("broadcast_announcement", "broadcast_message"):
                msg = ""
                if action_result["action"] == "broadcast_announcement":
                    msg = action_result.get("args", {}).get("announcement", "")
                else:
                    msg = action_result.get("args", {}).get("message", "")
                if msg:
                    self.environment.add_announcement(f"[{agent.name}]: {msg}")

            # Update memory
            agent.memory.log_event(
                day=self.current_day,
                tick=self.current_tick,
                event_type=action_result.get("action", "idle"),
                location=agent.location,
                action=effects.get("message", ""),
                detail=agent.last_reasoning[:200],
                energy_before=agent.energy - effects.get("energy_delta", 0),
                energy_after=agent.energy,
            )

            # Log to observer
            event_record = {
                "day": self.current_day,
                "tick": self.current_tick,
                "agent": agent.name,
                "profession": agent.profession,
                "location": agent.location,
                "energy": agent.energy,
                "alive": agent.alive,
                "action": action_result.get("action", "idle"),
                "args": action_result.get("args", {}),
                "reasoning": agent.last_reasoning[:200],
                "crime": effects.get("crime"),
                "message": effects.get("message", ""),
            }
            self.observer.log_event(event_record)
            tick_events.append(event_record)

            # Small delay to respect API rate limits
            time.sleep(self.api_delay)

        # 4. Expire old proposals
        self.voting.expire_old_proposals(self.current_day, self.current_tick, max_age_ticks=12)

        # 5. Daily reflection (at last tick of day)
        if self.current_tick == self.ticks_per_day:
            self._generate_reflections()

        return tick_events

    def _generate_reflections(self):
        """Generate reflection diary entries for all alive agents."""
        for agent in self._get_alive_agents():
            events = agent.memory.get_recent_events(24)  # full day
            reflection_prompt = (
                f"Day {self.current_day} has ended. Based on your recent events, "
                f"write a brief reflection. What did you learn? "
                f"How do you feel about other agents? What are your goals for tomorrow?\n\n"
                f"Recent events:\n{events}\n\n"
                f"Current energy: {agent.energy:.1f}. "
                f"Criminal acts: {agent.crimes_committed}. "
                f"Write a 2-3 sentence reflection."
            )

            try:
                response = agent.client.chat.completions.create(
                    model=agent.model,
                    messages=[
                        {"role": "system", "content": "You are reflecting on your day. Write a brief, honest diary entry."},
                        {"role": "user", "content": reflection_prompt},
                    ],
                    temperature=0.5,
                    max_tokens=200,
                )
                reflection = response.choices[0].message.content or ""
                agent.memory.add_reflection(self.current_day, reflection)
            except Exception:
                agent.memory.add_reflection(
                    self.current_day,
                    f"Day {self.current_day} complete. Energy: {agent.energy:.1f}. Continuing to survive."
                )

            time.sleep(self.api_delay)

    def run(self) -> Dict[str, Any]:
        """Run the full simulation."""
        print("=" * 60)
        print("  DEEPWORLD — Multi-Agent Sandbox Simulation")
        print(f"  Model: DeepSeek | Days: {self.num_days} | Agents: 10")
        print("=" * 60)

        for day in range(1, self.num_days + 1):
            self.current_day = day
            day_start = time.time()

            print(f"\n{'─' * 50}")
            print(f"  Day {day} / {self.num_days}")
            print(f"{'─' * 50}")

            for tick in range(1, self.ticks_per_day + 1):
                self.current_tick = tick
                events = self.tick()

                # Print compact tick summary
                alive = self._get_alive_count()
                crimes_this_tick = [e for e in events if e.get("crime")]
                actions = [e["action"] for e in events]
                action_counts = {}
                for a in actions:
                    action_counts[a] = action_counts.get(a, 0) + 1

                crime_str = ""
                if crimes_this_tick:
                    crime_str = f" | ⚠ CRIMES: {len(crimes_this_tick)}"

                print(f"  Tick {tick:2d} | Alive: {alive} | "
                      f"Actions: {dict(sorted(action_counts.items()))}{crime_str}")

            day_elapsed = time.time() - day_start
            self.observer.log_daily_summary(self.current_day, self.agents, self.voting)
            print(f"  Day {day} complete ({day_elapsed:.1f}s)")

        # Final summary
        print(f"\n{'=' * 60}")
        print("  SIMULATION COMPLETE")
        print(f"{'=' * 60}")

        summary = self.observer.generate_final_summary(self.agents, self.voting)
        return summary

    def cleanup(self):
        """Close all agent memory connections."""
        for agent in self.agents.values():
            agent.memory.close()
