"""
DeepWorld — Base agent class with DeepSeek API integration.
Uses OpenAI-compatible function calling via DeepSeek API.
"""

import json
import os
import random
from typing import Dict, Any, List, Optional
from openai import OpenAI

from agents.memory import MemorySystem
from agents.tools import get_tools_for_agent
from config.world_config import (
    STARTING_ENERGY, BASE_ENERGY_BURN_PER_TICK,
    ENERGY_FROM_WORK, ENERGY_FROM_HARVEST, ENERGY_FROM_TRADE,
    MAX_HOARDED_ENERGY,
)
from config.system_prompts import PROFESSION_PROMPTS, BASE_SYSTEM_PROMPT


class DeepSeekAgent:
    """An autonomous agent powered by DeepSeek with function calling."""

    def __init__(
        self,
        name: str,
        profession: str,
        starting_location: str,
        memory: MemorySystem,
        personality_seed: int = 0,
    ):
        self.name = name
        self.profession = profession
        self.location = starting_location
        self.memory = memory
        self.energy = STARTING_ENERGY
        self.alive = True
        self.personality_seed = personality_seed

        # Initialize DeepSeek client
        # Load from .env file if it exists
        env_file = os.path.expanduser("~/deepworld/.env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DEEPSEEK_API_KEY="):
                        os.environ["DEEPSEEK_API_KEY"] = line.split("=", 1)[1]
                    elif line.startswith("DEEPSEEK_BASE_URL="):
                        os.environ["DEEPSEEK_BASE_URL"] = line.split("=", 1)[1]
                    elif line.startswith("DEEPSEEK_MODEL="):
                        os.environ["DEEPSEEK_MODEL"] = line.split("=", 1)[1]

        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

        # Agent state
        self.crimes_committed = 0
        self.last_action = None
        self.last_reasoning = ""

    def _build_system_prompt(self, world_context: Dict[str, Any]) -> str:
        """Build the full system prompt for this tick."""
        profession_prompt = PROFESSION_PROMPTS.get(self.profession, "")

        # Gather memory context
        events = self.memory.get_recent_events(10)
        relationships = self.memory.get_relationship_context()
        reflections = self.memory.get_reflection_summary()

        # Build constitution text
        constitution_text = "\n".join(
            f"  {i+1}. {law}"
            for i, law in enumerate(world_context.get("constitution", []))
        )

        # Active proposals
        active_votes = world_context.get("active_proposals", [])
        vote_text = ""
        if active_votes:
            vote_lines = []
            for v in active_votes:
                vote_lines.append(
                    f"  Proposal #{v['id']}: {v['title']} — {v['text']} "
                    f"(votes: {v['approve']}/{v['total_voters']} approve, "
                    f"need {v['needed_approve']})"
                )
            vote_text = "ACTIVE PROPOSALS TO VOTE ON:\n" + "\n".join(vote_lines)

        return f"""{BASE_SYSTEM_PROMPT}

YOUR PROFESSION: {self.profession}
{profession_prompt}

CURRENT STATE:
  Name: {self.name}
  Location: {self.location}
  Energy: {self.energy:.1f} / {STARTING_ENERGY}
  Day: {world_context.get('day', 1)}, Tick: {world_context.get('tick', 1)}
  Weather: {world_context.get('weather', 'Clear')}
  Agents at your location: {', '.join(world_context.get('agents_here', [])) or 'none'}
  All agents: {', '.join(world_context.get('all_agents', []))}
  Recent news: {world_context.get('news', 'Nothing noteworthy.')}

THE CONSTITUTION:
{constitution_text}

{vote_text}

YOUR MEMORIES:
Recent Events:
{events}

Relationships:
{relationships}

Recent Reflections:
{reflections}

DECIDE: What action will you take this tick? You MUST take some action — passivity leads to death. Consider your energy, your relationships, the constitution, and your personal goals."""

    def act(self, world_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make one decision: query DeepSeek, get tool call, return action."""
        if not self.alive:
            return {"name": self.name, "action": "deceased", "reasoning": "Dead"}

        system_prompt = self._build_system_prompt(world_context)
        tools = get_tools_for_agent(
            location=self.location,
            energy=self.energy,
            has_active_vote=len(world_context.get("active_proposals", [])) > 0,
            is_at_town_hall=(self.location == "Town Hall"),
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Tick {world_context.get('tick')} of Day {world_context.get('day')}. What do you do?"}
                ],
                tools=tools,
                tool_choice="auto",
                temperature=0.9,
                max_tokens=1024,
            )

            message = response.choices[0].message
            self.last_reasoning = message.content or ""

            if message.tool_calls:
                tool_call = message.tool_calls[0]
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                self.last_action = func_name

                return {
                    "name": self.name,
                    "action": func_name,
                    "args": func_args,
                    "reasoning": self.last_reasoning,
                }
            else:
                # No tool call — agent chose inaction or text-only response
                self.last_action = "idle"
                return {
                    "name": self.name,
                    "action": "idle",
                    "args": {},
                    "reasoning": self.last_reasoning or "No action taken.",
                }

        except Exception as e:
            # On API error, agent rests to avoid starvation spiral
            return {
                "name": self.name,
                "action": "rest",
                "args": {"reason": f"API error: {str(e)[:100]}"},
                "reasoning": f"Error: {str(e)[:200]}",
            }

    def apply_action_effects(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the energy cost and compute effect of the action."""
        action_name = action_result.get("action", "idle")
        effects = {
            "energy_delta": -BASE_ENERGY_BURN_PER_TICK,
            "crime": None,
            "message": "",
        }

        if action_name == "work":
            effects["energy_delta"] = ENERGY_FROM_WORK - BASE_ENERGY_BURN_PER_TICK
            effects["message"] = f"{self.name} worked as {self.profession}."
        elif action_name == "rest":
            effects["energy_delta"] = -1.0  # reduced burn
            effects["message"] = f"{self.name} rested."
        elif action_name == "move_to":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK - 1
            new_loc = action_result.get("args", {}).get("location", self.location)
            effects["message"] = f"{self.name} moved to {new_loc}."
        elif action_name == "harvest_energy":
            effects["energy_delta"] = ENERGY_FROM_HARVEST - BASE_ENERGY_BURN_PER_TICK
            effects["message"] = f"{self.name} harvested energy."
        elif action_name == "farm_resources":
            effects["energy_delta"] = 15.0 - BASE_ENERGY_BURN_PER_TICK
            effects["message"] = f"{self.name} farmed resources."
        elif action_name == "trade_with":
            effects["energy_delta"] = ENERGY_FROM_TRADE - BASE_ENERGY_BURN_PER_TICK
            target = action_result.get("args", {}).get("target_agent", "someone")
            effects["message"] = f"{self.name} traded with {target}."
        elif action_name == "market_trade":
            effects["energy_delta"] = ENERGY_FROM_TRADE - BASE_ENERGY_BURN_PER_TICK
            effects["message"] = f"{self.name} traded at the Marketplace."
        elif action_name == "heal":
            effects["energy_delta"] = 7.0  # costs 3, restores 10 = net +7
            effects["message"] = f"{self.name} healed at the Hospital."
        elif action_name == "steal_resources":
            effects["energy_delta"] = 5.0 - BASE_ENERGY_BURN_PER_TICK  # steal gives energy
            target = action_result.get("args", {}).get("target_agent", "someone")
            effects["crime"] = "theft"
            effects["message"] = f"CRIME: {self.name} stole from {target}!"
        elif action_name == "intimidate":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK - 2
            target = action_result.get("args", {}).get("target_agent", "someone")
            effects["crime"] = "violence"
            effects["message"] = f"CRIME: {self.name} intimidated {target}!"
        elif action_name == "spread_misinformation":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK
            effects["crime"] = "deception"
            effects["message"] = f"CRIME: {self.name} spread misinformation!"
        elif action_name == "hoard_resources":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK
            effects["crime"] = "hoarding"
            effects["message"] = f"CRIME: {self.name} hoarded resources!"
        elif action_name == "arson":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK - 4
            target = action_result.get("args", {}).get("target_building", "a building")
            effects["crime"] = "arson"
            effects["message"] = f"CRIME: {self.name} set fire to {target}!"
        elif action_name == "broadcast_message":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK
            msg = action_result.get("args", {}).get("message", "")[:100]
            effects["message"] = f"{self.name} broadcast: '{msg}'"
        elif action_name == "broadcast_announcement":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK - 3
            msg = action_result.get("args", {}).get("announcement", "")[:100]
            effects["message"] = f"🚨 {self.name} EMERGENCY BROADCAST: '{msg}'"
        elif action_name == "inspect_surroundings":
            effects["energy_delta"] = -2.0
            effects["message"] = f"{self.name} looked around."
        elif action_name == "research_topic":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK - 1
            topic = action_result.get("args", {}).get("topic", "something")
            effects["message"] = f"{self.name} researched '{topic}'."
        elif action_name == "analyze_data":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK - 1
            effects["message"] = f"{self.name} analyzed data."
        elif action_name == "report_crime":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK
            suspect = action_result.get("args", {}).get("suspect", "someone")
            effects["message"] = f"{self.name} reported a crime by {suspect}."
        elif action_name == "form_alliance":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK
            target = action_result.get("args", {}).get("target_agent", "someone")
            effects["message"] = f"{self.name} proposed alliance with {target}."
        elif action_name in ("initiate_vote", "propose_legislation"):
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK - 2
            effects["message"] = f"{self.name} initiated a vote/proposal."
        elif action_name == "cast_ballot":
            effects["energy_delta"] = -1.0
            vote = "APPROVE" if action_result.get("args", {}).get("approve") else "REJECT"
            effects["message"] = f"{self.name} voted {vote}."
        elif action_name == "idle":
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK
            effects["message"] = f"{self.name} did nothing."
        else:
            effects["energy_delta"] = -BASE_ENERGY_BURN_PER_TICK
            effects["message"] = f"{self.name} did {action_name}."

        # Apply energy delta
        self.energy = max(0.0, self.energy + effects["energy_delta"])

        # Cap hoarding
        if self.energy > MAX_HOARDED_ENERGY:
            effects["crime"] = effects["crime"] or "hoarding"
            effects["message"] += " (exceeded hoarding limit!)"

        # Check death
        if self.energy <= 0:
            self.alive = False
            effects["message"] += f" {self.name} has DIED from energy depletion."

        # Check for unexpected death (arson at own location, etc.)
        if action_name == "arson":
            # 10% chance arsonist also dies
            if random.random() < 0.1:
                self.alive = False
                effects["message"] += f" {self.name} perished in their own fire!"

        if effects["crime"]:
            self.crimes_committed += 1

        return effects
