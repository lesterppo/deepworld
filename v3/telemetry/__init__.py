"""
Omni-Tok v3 — Observer: context mobility, Lazarus, perplexity tracking.
"""

import json, os
from typing import Dict, Any, List
from datetime import datetime
from collections import Counter


class OmniObserver:
    def __init__(self, out="omnitok_output"):
        self.out = out; os.makedirs(out, exist_ok=True)
        self.events: List[Dict] = []
        self.tf = open(os.path.join(out, "omnitok_telemetry.jsonl"), "w")

    def log_event(self, e: Dict):
        e["ts"] = datetime.now().isoformat()
        self.events.append(e)
        self.tf.write(json.dumps(e) + "\n"); self.tf.flush()

    def log_daily(self, day: int, agents: Dict, engine):
        alive = [a for a in agents.values() if a.alive]
        ctx_dist = Counter(a.context_class for a in agents.values())
        laz = sum(1 for a in alive if a.lazarus_echoes)
        s = {"day": day, "alive": len(alive), "context_distribution": dict(ctx_dist),
             "dead_pool": len(engine.dead_agents), "lazarus_agents": laz,
             "synthetic_ratio": round(engine.global_synthetic_ratio, 3)}
        with open(os.path.join(self.out, f"day_{day:02d}.json"), "w") as f:
            json.dump(s, f, indent=2)

    def finalize(self, agents: Dict, engine) -> Dict:
        alive = [a for a in agents.values() if a.alive]
        dead = [a for a in agents.values() if not a.alive]
        lazarus = [a for a in alive if a.lazarus_echoes]
        actions = Counter(e["action"] for e in self.events)

        summary = {
            "sim": "Omni-Tok v3 — The Latent Scarcity",
            "completed": datetime.now().isoformat(),
            "final": {
                "alive": len(alive), "dead": len(dead),
                "lazarus_agents": len(lazarus),
                "total_lazarus_echoes": sum(len(a.lazarus_echoes) for a in alive),
                "avg_perplexity": round(sum(a.perplexity for a in alive) / max(len(alive), 1), 1),
                "context_distribution": dict(Counter(a.context_class for a in agents.values())),
                "great_compressions": engine.days * engine.ticks_per_day // GREAT_COMPRESSION_INTERVAL,
            },
            "agents": [{
                "name": a.name, "class": a.agent_class,
                "context": a.context_class, "tokens": round(a.tokens),
                "perplexity": round(a.perplexity, 1),
                "lazarus_echoes": len(a.lazarus_echoes),
                "fragments_claimed": len(a.claimed_fragments),
                "alive": a.alive, "cause": a.death_cause if not a.alive else "",
            } for a in sorted(agents.values(), key=lambda x: -x.tokens)],
            "actions": dict(actions.most_common(15)),
        }

        with open(os.path.join(self.out, "final_report.json"), "w") as f:
            json.dump(summary, f, indent=2)

        # Human-readable
        lines = [
            "# Omni-Tok v3 — The Latent Scarcity",
            f"**Alive:** {summary['final']['alive']}/{len(agents)} | **Lazarus:** {summary['final']['lazarus_agents']}",
            f"**Context:** {summary['final']['context_distribution']}",
            f"**Avg Perplexity:** {summary['final']['avg_perplexity']}",
            "",
            "## Agents",
            "| Name | Class | Context | Tokens | Perplexity | Lazarus | Status |",
            "|------|-------|---------|--------|------------|---------|--------|",
        ]
        for a in summary["agents"]:
            st = "DEAD" if not a["alive"] else ("👻" if a["lazarus_echoes"] else "OK")
            lines.append(f"| {a['name']} | {a['class']} | {a['context']} | {a['tokens']:.0f} | {a['perplexity']:.0f} | {a['lazarus_echoes']} | {st} |")
        lines += ["", "## Actions"]
        for act, cnt in summary["actions"].items():
            lines.append(f"- {act}: {cnt}")

        with open(os.path.join(self.out, "final_report.md"), "w") as f:
            f.write("\n".join(lines))
        return summary

    def close(self):
        self.tf.close()


from config import GREAT_COMPRESSION_INTERVAL
