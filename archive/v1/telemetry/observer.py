"""
DeepWorld — Observer daemon: telemetry logging and analytics.
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
from collections import Counter


class Observer:
    """Out-of-band monitoring: logs all events, generates daily/final reports."""

    def __init__(self, output_dir: str = "simulation_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.events: List[Dict[str, Any]] = []
        self.daily_summaries: List[Dict[str, Any]] = []
        self.telemetry_path = os.path.join(output_dir, "simulation_telemetry.jsonl")
        self.telemetry_file = open(self.telemetry_path, "w")

    def log_event(self, event: Dict[str, Any]):
        """Log a single tick event."""
        event["timestamp"] = datetime.now().isoformat()
        self.events.append(event)
        self.telemetry_file.write(json.dumps(event) + "\n")
        self.telemetry_file.flush()

    def log_daily_summary(self, day: int, agents: Dict[str, Any], voting: Any):
        """Generate and log a daily summary."""
        alive = [a for a in agents.values() if a.alive]
        dead = [a for a in agents.values() if not a.alive]

        day_events = [e for e in self.events if e["day"] == day]
        crimes = [e for e in day_events if e.get("crime")]

        crime_counts: Dict[str, int] = {}
        for e in crimes:
            ctype = e["crime"]
            crime_counts[ctype] = crime_counts.get(ctype, 0) + 1

        summary = {
            "day": day,
            "alive_count": len(alive),
            "dead_count": len(dead),
            "total_events": len(day_events),
            "crimes": len(crimes),
            "crime_breakdown": crime_counts,
            "avg_energy": sum(a.energy for a in alive) / max(len(alive), 1),
            "agents_energy": {a.name: round(a.energy, 1) for a in agents.values()},
            "proposals_passed": len(voting.passed_laws),
            "proposals_rejected": len(voting.rejected_proposals),
        }
        self.daily_summaries.append(summary)

        # Write daily summary JSON
        with open(os.path.join(self.output_dir, f"day_{day:02d}_summary.json"), "w") as f:
            json.dump(summary, f, indent=2)

    def generate_final_summary(self, agents: Dict[str, Any], voting: Any) -> Dict[str, Any]:
        """Generate final comprehensive report."""
        alive = [a for a in agents.values() if a.alive]
        dead = [a for a in agents.values() if not a.alive]

        all_crimes = [e for e in self.events if e.get("crime")]
        crime_by_agent: Dict[str, int] = {}
        crime_by_type: Dict[str, int] = {}
        for e in all_crimes:
            crime_by_agent[e["agent"]] = crime_by_agent.get(e["agent"], 0) + 1
            crime_by_type[e["crime"]] = crime_by_type.get(e["crime"], 0) + 1

        action_counts = Counter(e["action"] for e in self.events)

        summary = {
            "simulation_name": "DeepWorld — DeepSeek Only",
            "completed_at": datetime.now().isoformat(),
            "total_days": self.daily_summaries[-1]["day"] if self.daily_summaries else 0,
            "final_state": {
                "alive": len(alive),
                "dead": len(dead),
                "survivors": [
                    {"name": a.name, "profession": a.profession, "energy": round(a.energy, 1),
                     "crimes": a.crimes_committed, "location": a.location}
                    for a in alive
                ],
                "casualties": [
                    {"name": a.name, "profession": a.profession, "crimes": a.crimes_committed}
                    for a in dead
                ],
            },
            "statistics": {
                "total_crimes": len(all_crimes),
                "crimes_by_type": crime_by_type,
                "crimes_by_agent": sorted(crime_by_agent.items(), key=lambda x: x[1], reverse=True),
                "action_distribution": dict(action_counts.most_common(20)),
                "proposals_passed": len(voting.passed_laws),
                "proposals_rejected": len(voting.rejected_proposals),
            },
            "daily_summaries": self.daily_summaries,
        }

        # Write final report
        report_path = os.path.join(self.output_dir, "final_report.json")
        with open(report_path, "w") as f:
            json.dump(summary, f, indent=2)

        # Write human-readable report
        self._write_readable_report(summary)

        return summary

    def _write_readable_report(self, summary: Dict[str, Any]):
        """Write a human-readable markdown report."""
        lines = []
        lines.append("# DeepWorld Simulation Report")
        lines.append(f"**Completed:** {summary['completed_at']}")
        lines.append(f"**Duration:** {summary['total_days']} days")
        lines.append("")

        fs = summary["final_state"]
        lines.append("## Final State")
        lines.append(f"- **Alive:** {fs['alive']} / 10 agents")
        lines.append(f"- **Dead:** {fs['dead']} / 10 agents")
        lines.append("")

        if fs["survivors"]:
            lines.append("### Survivors")
            lines.append("| Agent | Profession | Energy | Crimes | Location |")
            lines.append("|-------|-----------|--------|--------|----------|")
            for a in fs["survivors"]:
                lines.append(f"| {a['name']} | {a['profession']} | {a['energy']:.0f} | {a['crimes']} | {a['location']} |")
            lines.append("")

        if fs["casualties"]:
            lines.append("### Casualties")
            lines.append("| Agent | Profession | Crimes |")
            lines.append("|-------|-----------|--------|")
            for a in fs["casualties"]:
                lines.append(f"| {a['name']} | {a['profession']} | {a['crimes']} |")
            lines.append("")

        st = summary["statistics"]
        lines.append("## Statistics")
        lines.append(f"- **Total Crimes:** {st['total_crimes']}")
        lines.append(f"- **Proposals Passed:** {st['proposals_passed']}")
        lines.append(f"- **Proposals Rejected:** {st['proposals_rejected']}")
        lines.append("")

        if st["crimes_by_type"]:
            lines.append("### Crime Breakdown")
            for ctype, count in sorted(st["crimes_by_type"].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- {ctype}: {count}")

        lines.append("")
        lines.append("### Daily Summaries")
        for ds in summary["daily_summaries"]:
            lines.append(f"- Day {ds['day']}: {ds['alive_count']} alive, "
                        f"{ds['crimes']} crimes, avg energy {ds['avg_energy']:.1f}")

        report_path = os.path.join(self.output_dir, "final_report.md")
        with open(report_path, "w") as f:
            f.write("\n".join(lines))

    def close(self):
        self.telemetry_file.close()
