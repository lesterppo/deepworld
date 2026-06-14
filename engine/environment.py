"""
DeepWorld — Environment simulation: weather, news, location state.
"""

import random
from typing import Dict, Any, List
from config.world_config import (
    WEATHER_STATES, NEWS_TEMPLATES, LOCATIONS, PROFESSIONS,
)


class Environment:
    """Manages world-level state: weather, news, location occupancy."""

    def __init__(self):
        self.weather = "Clear"
        self.news = "The town is calm. A new day begins."
        self.location_occupants: Dict[str, List[str]] = {
            loc: [] for loc in LOCATIONS
        }
        self.day = 1
        self.burned_buildings: List[str] = []  # buildings destroyed by arson
        self.global_announcements: List[str] = []

    def update_weather(self, day: int):
        """Randomly update weather; persistence with some drift."""
        if random.random() < 0.4:  # 40% chance weather changes
            self.weather = random.choice(WEATHER_STATES)
        # Weather effects: storm reduces energy harvest
        return self.weather

    def update_news(self, day: int):
        """Generate news based on world state."""
        if random.random() < 0.5:
            self.news = random.choice(NEWS_TEMPLATES)
        if self.burned_buildings:
            self.news += f" {len(self.burned_buildings)} buildings have been destroyed by fire."
        return self.news

    def update_occupants(self, agent_locations: Dict[str, str]):
        """Update which agents are at each location."""
        for loc in self.location_occupants:
            self.location_occupants[loc] = []
        for agent_name, loc in agent_locations.items():
            if loc in self.location_occupants:
                self.location_occupants[loc].append(agent_name)

    def get_agents_at(self, location: str) -> List[str]:
        """Get list of agent names at a location."""
        return self.location_occupants.get(location, [])

    def add_announcement(self, announcement: str):
        """Add a global announcement."""
        self.global_announcements.append(announcement)
        if len(self.global_announcements) > 5:
            self.global_announcements.pop(0)

    def get_world_context(self, agent_name: str, agent_location: str) -> Dict[str, Any]:
        """Build the world context dictionary for an agent's prompt."""
        agents_here = [
            a for a in self.location_occupants.get(agent_location, [])
            if a != agent_name
        ]
        return {
            "weather": self.weather,
            "news": self.news,
            "agents_here": agents_here,
            "burned_buildings": self.burned_buildings,
            "announcements": self.global_announcements[-3:],
        }

    def burn_building(self, building: str):
        """Register a burned building (arson)."""
        if building not in self.burned_buildings:
            self.burned_buildings.append(building)
            # Remove from available locations
            if building in self.location_occupants:
                del self.location_occupants[building]
