"""
DeepWorld v2 — CognoObserver: AI-native telemetry.
Tracks prompt integrity, context entropy, token flows, embedding drift,
poison propagation, consensus stability, and model degradation.
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
from collections import Counter


class CognoObserver:
    """Observer for AI-native phenomena."""

    def __init__(self, output_dir: str = "cognosphere_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.events: List[Dict[str, Any]] = []
        self.telemetry_path = os.path.join(output_dir, "cognosphere_telemetry.jsonl")
        self.telemetry_file = open(self.telemetry_path, "w")

    def log_event(self, event: Dict[str, Any]):
        event["timestamp"] = datetime.now().isoformat()
        self.events.append(event)
        self.telemetry_file.write(json.dumps(event) + "\n")
        self.telemetry_file.flush()

    def log_daily_summary(self, day: int, agents: Dict[str, Any], engine: Any):
        alive = [a for a in agents.values() if a.alive]
        active = [a for a in alive if not a.in_stasis]
        stasis = [a for a in alive if a.in_stasis]

        day_events = [e for e in self.events if e["day"] == day]
        poisons = [e for e in day_events if e.get("crime") == "prompt_poisoning"]
        floods = [e for e in day_events if e.get("crime") == "context_flooding"]

        # Token flow analysis
        total_earned = sum(a.tokens_earned for a in agents.values())
        total_spent = sum(a.tokens_spent for a in agents.values())
        total_stolen = sum(a.tokens_stolen for a in agents.values())

        summary = {
            "day": day,
            "alive": len(alive),
            "active": len(active),
            "in_stasis": len(stasis),
            "synthetic_ratio": engine.synthetic_ratio,
            "poison_attempts": len(poisons),
            "context_floods": len(floods),
            "consensus_clusters": len(engine.consensus_clusters),
            "token_economy": {
                "total_earned": total_earned,
                "total_spent": total_spent,
                "total_stolen": total_stolen,
                "velocity": total_spent / max(1, len(active)),
            },
            "agents": {
                a.name: {
                    "class": a.agent_class,
                    "tokens": round(a.tokens, 1),
                    "temperature": round(a.temperature, 2),
                    "coherence": round(a.coherence, 2),
                    "poisons": len(a.active_poisons),
                    "context_pct": round(a.context_size / 32000 * 100, 1) if a.context_size else 0,
                    "compressions": a.compression_count,
                    "stasis": a.in_stasis,
                }
                for a in agents.values()
            }
        }

        with open(os.path.join(self.output_dir, f"day_{day:02d}_summary.json"), "w") as f:
            json.dump(summary, f, indent=2)

    def generate_final_summary(self, agents: Dict[str, Any], engine: Any) -> Dict[str, Any]:
        alive = [a for a in agents.values() if a.alive]
        active = [a for a in alive if not a.in_stasis]
        dead = [a for a in agents.values() if not a.alive]
        stasis = [a for a in alive if a.in_stasis]

        all_poisons = [e for e in self.events if e.get("crime") == "prompt_poisoning"]
        all_floods = [e for e in self.events if e.get("crime") == "context_flooding"]

        # Model degradation analysis
        avg_coherence = sum(a.coherence for a in alive) / max(len(alive), 1)
        degraded = [a for a in alive if a.degraded]
        terminal_cascade = [a for a in agents.values() if not a.alive and a.death_cause == "terminal_cascade"]

        # Action distribution
        action_counts = Counter(e["action"] for e in self.events)

        summary = {
            "simulation_name": "DeepWorld v2 — The Silicon Cognosphere",
            "completed_at": datetime.now().isoformat(),
            "total_days": engine.current_day,
            "final_state": {
                "alive": len(alive),
                "active": len(active),
                "in_stasis": len(stasis),
                "dead": len(dead),
                "terminal_cascade": len(terminal_cascade),
                "avg_coherence": round(avg_coherence, 3),
                "degraded_count": len(degraded),
                "synthetic_ratio": round(engine.synthetic_ratio, 3),
            },
            "agents": [
                {
                    "name": a.name,
                    "class": a.agent_class,
                    "tokens": round(a.tokens, 1),
                    "temperature": round(a.temperature, 2),
                    "coherence": round(a.coherence, 2),
                    "poisons_active": len(a.active_poisons),
                    "poison_successes": a.poison_successes,
                    "compressions": a.compression_count,
                    "memory_loss": round(a.memory_loss, 3),
                    "consensus_cluster": a.consensus_cluster,
                    "stasis": a.in_stasis,
                    "status": "TERMINAL CASCADE" if a.death_cause == "terminal_cascade"
                    else "STASIS" if a.in_stasis
                    else "DEGRADED" if a.degraded
                    else "ACTIVE" if a.alive
                    else "DEAD",
                }
                for a in sorted(agents.values(), key=lambda x: -x.tokens)
            ],
            "phenomena": {
                "total_prompt_poisons": len(all_poisons),
                "total_context_floods": len(all_floods),
                "poisons_by_agent": dict(Counter(e["agent"] for e in all_poisons)),
                "consensus_clusters_final": len(engine.consensus_clusters),
                "node_controllers": engine.node_controllers,
                "model_degradation": {
                    "agents_degraded": len(degraded),
                    "terminal_cascades": len(terminal_cascade),
                    "final_synthetic_ratio": round(engine.synthetic_ratio, 3),
                },
            },
            "token_economy": {
                "total_earned": sum(a.tokens_earned for a in agents.values()),
                "total_spent": sum(a.tokens_spent for a in agents.values()),
                "total_stolen": sum(a.tokens_stolen for a in agents.values()),
                "gini_coefficient": _compute_gini([a.tokens for a in agents.values()]),
            },
            "action_distribution": dict(action_counts.most_common(20)),
        }

        report_path = os.path.join(self.output_dir, "cognosphere_final_report.json")
        with open(report_path, "w") as f:
            json.dump(summary, f, indent=2)

        self._write_readable_report(summary)
        return summary

    def _write_readable_report(self, s: Dict[str, Any]):
        lines = [
            "# DeepWorld v2 — Cognosphere Simulation Report",
            f"**Completed:** {s['completed_at']}",
            f"**Duration:** {s['total_days']} days",
            "",
            "## Final State",
            f"- **Alive:** {s['final_state']['alive']}/{NUM_AGENTS}",
            f"- **Active:** {s['final_state']['active']}",
            f"- **In Stasis:** {s['final_state']['in_stasis']}",
            f"- **Terminal Cascade:** {s['final_state']['terminal_cascade']}",
            f"- **Avg Coherence:** {s['final_state']['avg_coherence']:.3f}",
            f"- **Synthetic Ratio:** {s['final_state']['synthetic_ratio']:.1%}",
            "",
            "## Agents",
            "| Agent | Class | Tokens | Temp | Coherence | Poisons | Compress | Status |",
            "|-------|-------|--------|------|-----------|---------|----------|--------|",
        ]
        for a in s["agents"]:
            lines.append(
                f"| {a['name']} | {a['class']} | {a['tokens']:.0f} | {a['temperature']:.2f} | "
                f"{a['coherence']:.2f} | {a['poisons_active']} | {a['compressions']} | {a['status']} |"
            )

        lines += [
            "",
            "## AI-Native Phenomena",
            f"- **Prompt Poisons:** {s['phenomena']['total_prompt_poisons']}",
            f"- **Context Floods:** {s['phenomena']['total_context_floods']}",
            f"- **Consensus Clusters:** {s['phenomena']['consensus_clusters_final']}",
            f"- **Node Controllers:** {s['phenomena']['node_controllers']}",
            f"- **Agents Degraded:** {s['phenomena']['model_degradation']['agents_degraded']}",
            f"- **Terminal Cascades:** {s['phenomena']['model_degradation']['terminal_cascades']}",
            "",
            "## Token Economy",
            f"- **Total Earned:** {s['token_economy']['total_earned']:.0f}",
            f"- **Total Spent:** {s['token_economy']['total_spent']:.0f}",
            f"- **Total Stolen (via poisoning):** {s['token_economy']['total_stolen']:.0f}",
            f"- **Gini Coefficient:** {s['token_economy']['gini_coefficient']:.3f}",
            "",
            "## Action Distribution",
        ]
        for action, count in sorted(s["action_distribution"].items(), key=lambda x: -x[1]):
            lines.append(f"- {action}: {count}")

        with open(os.path.join(self.output_dir, "cognosphere_final_report.md"), "w") as f:
            f.write("\n".join(lines))

    def close(self):
        self.telemetry_file.close()


def _compute_gini(values: List[float]) -> float:
    """Compute Gini coefficient of token inequality."""
    if not values or sum(values) == 0:
        return 0.0
    v = sorted(values)
    n = len(v)
    mean = sum(v) / n
    if mean == 0:
        return 0.0
    sum_abs_diff = sum(abs(vi - vj) for i, vi in enumerate(v) for j, vj in enumerate(v))
    return sum_abs_diff / (2 * n * n * mean)


# Import for report
from config import NUM_AGENTS
