"""
DeepWorld — 3-tier memory system.
Mirrors Emergence AI: event ledger, reflection diary, relationship matrix.
Uses SQLite for events, JSON for reflections/relationships (lightweight for 10 agents).
"""

import json
import sqlite3
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime


class MemorySystem:
    """Per-agent memory with three tiers."""

    def __init__(self, agent_id: str, db_path: str = "deepworld_memory.db"):
        self.agent_id = agent_id
        self.db_path = db_path
        self._init_db()

        # Tier 2: Reflection diary (in-memory list of dicts)
        self.reflections: List[Dict[str, Any]] = []

        # Tier 3: Relationship matrix (agent_name -> relationship data)
        self.relationships: Dict[str, Dict[str, Any]] = {}

    def _init_db(self):
        """Initialize the SQLite event ledger."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                day INTEGER NOT NULL,
                tick INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                location TEXT,
                action TEXT,
                detail TEXT,
                energy_before REAL,
                energy_after REAL
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_agent_day
            ON events(agent_id, day)
        """)
        self.conn.commit()

    def log_event(
        self,
        day: int,
        tick: int,
        event_type: str,
        location: str = "",
        action: str = "",
        detail: str = "",
        energy_before: float = 0,
        energy_after: float = 0,
    ):
        """Tier 1: Log a timestamped event."""
        self.conn.execute(
            """INSERT INTO events (agent_id, day, tick, timestamp, event_type, location, action, detail, energy_before, energy_after)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (self.agent_id, day, tick, datetime.now().isoformat(), event_type,
             location, action, detail, energy_before, energy_after)
        )
        self.conn.commit()

    def add_reflection(self, day: int, content: str):
        """Tier 2: Add a reflection diary entry."""
        self.reflections.append({
            "day": day,
            "timestamp": datetime.now().isoformat(),
            "content": content,
        })
        # Keep only last 20 reflections
        if len(self.reflections) > 20:
            self.reflections = self.reflections[-20:]

    def update_relationship(self, target_agent: str, update: Dict[str, Any]):
        """Tier 3: Update relationship with another agent."""
        if target_agent not in self.relationships:
            self.relationships[target_agent] = {
                "trust": 0.5,
                "interactions": 0,
                "last_interaction": None,
                "notes": [],
                "status": "neutral",  # neutral, friend, enemy, ally, lover
            }

        rel = self.relationships[target_agent]
        rel["interactions"] += 1
        rel["last_interaction"] = datetime.now().isoformat()

        if "trust_delta" in update:
            rel["trust"] = max(0.0, min(1.0, rel["trust"] + update["trust_delta"]))
        if "status" in update:
            rel["status"] = update["status"]
        if "note" in update:
            day_str = str(update.get("day", "?"))
            rel["notes"].append("[Day " + day_str + "] " + update["note"])
            if len(rel["notes"]) > 10:
                rel["notes"] = rel["notes"][-10:]

    def get_relationship_context(self) -> str:
        """Get compact relationship summary for prompt injection."""
        if not self.relationships:
            return "No relationships formed yet."

        lines = []
        for agent, rel in sorted(self.relationships.items(),
                                  key=lambda x: x[1]["interactions"], reverse=True):
            trust_emoji = "🟢" if rel["trust"] > 0.6 else "🟡" if rel["trust"] > 0.3 else "🔴"
            lines.append(
                f"  {trust_emoji} {agent}: {rel['status']} "
                f"(trust={rel['trust']:.2f}, {rel['interactions']} interactions)"
            )
        return "\n".join(lines)

    def get_recent_events(self, limit: int = 10) -> str:
        """Get recent events for prompt injection."""
        cursor = self.conn.execute(
            """SELECT day, tick, event_type, location, action, detail, energy_before, energy_after
               FROM events WHERE agent_id = ?
               ORDER BY id DESC LIMIT ?""",
            (self.agent_id, limit)
        )
        rows = cursor.fetchall()
        if not rows:
            return "No events yet."

        lines = []
        for row in reversed(rows):
            day, tick, etype, loc, action, detail, eb, ea = row
            lines.append(f"  Day{day}.{tick:02d} [{etype}] @ {loc}: {action or detail} (E: {eb:.0f}→{ea:.0f})")
        return "\n".join(lines)

    def get_reflection_summary(self) -> str:
        """Get recent reflections for prompt injection."""
        if not self.reflections:
            return "No reflections yet."
        recent = self.reflections[-3:]
        return "\n".join(f"  Day {r['day']}: {r['content'][:200]}" for r in recent)

    def close(self):
        self.conn.close()
