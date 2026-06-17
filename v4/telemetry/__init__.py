"""
DeepWorld v4 — OmniObserverV4
==============================
Extended telemetry with tensor economy, cross-model tracking,
ontology statistics, and concept mining metrics.
"""
import json, os
from typing import Dict, Any, List
from datetime import datetime
from collections import Counter


class OmniObserverV4:
    def __init__(self, out="omnitok_v4_output"):
        self.out = out
        os.makedirs(out, exist_ok=True)
        self.events: List[Dict] = []
        self.tf = open(os.path.join(out, "omnitok_telemetry.jsonl"), "w")

    def log_event(self, e: Dict):
        e["ts"] = datetime.now().isoformat()
        self.events.append(e)
        self.tf.write(json.dumps(e) + "\n")
        self.tf.flush()

    def log_daily(self, day: int, agents: Dict, engine):
        alive = [a for a in agents.values() if a.alive]
        ctx_dist = Counter(a.context_class for a in agents.values())
        laz = sum(1 for a in alive if a.lazarus_echoes)
        model_dist = Counter(a.model_family for a in agents.values())
        
        # Tensor stats
        total_sent = sum(a.tensor_sent for a in agents.values())
        total_recv = sum(a.tensor_received for a in agents.values())
        total_concepts = sum(len(a.owned_concepts) for a in agents.values())
        
        s = {
            "day": day,
            "alive": len(alive),
            "context_distribution": dict(ctx_dist),
            "model_distribution": dict(model_dist),
            "dead_pool": len(engine.dead_agents),
            "lazarus_agents": laz,
            "synthetic_ratio": round(engine.global_synthetic_ratio, 3),
            "tensor_sent": total_sent,
            "tensor_received": total_recv,
            "concepts_owned": total_concepts,
            "tensor_messages_total": engine.tensor_messages_sent,
        }
        with open(os.path.join(self.out, f"day_{day:02d}.json"), "w") as f:
            json.dump(s, f, indent=2)

    def finalize(self, agents: Dict, engine) -> Dict:
        alive = [a for a in agents.values() if a.alive]
        dead = [a for a in agents.values() if not a.alive]
        lazarus = [a for a in alive if a.lazarus_echoes]
        actions = Counter(e["action"] for e in self.events)
        model_dist = Counter(a.model_family for a in agents.values())
        
        # Tensor stats
        total_sent = sum(a.tensor_sent for a in agents.values())
        total_recv = sum(a.tensor_received for a in agents.values())
        total_concepts = sum(len(a.owned_concepts) for a in agents.values())
        total_projections = sum(len(a.trained_projections) for a in agents.values())

        summary = {
            "sim": "DeepWorld v4 — Tensor-Native Cognosphere",
            "completed": datetime.now().isoformat(),
            "final": {
                "alive": len(alive), "dead": len(dead),
                "lazarus_agents": len(lazarus),
                "total_lazarus_echoes": sum(len(a.lazarus_echoes) for a in alive),
                "avg_perplexity": round(sum(a.perplexity for a in alive) / max(len(alive), 1), 1),
                "context_distribution": dict(Counter(a.context_class for a in agents.values())),
                "model_distribution": dict(model_dist),
                "great_compressions": engine.days * engine.ticks_per_day // 16,
                "tensor_sent": total_sent,
                "tensor_received": total_recv,
                "concepts_owned": total_concepts,
                "projections_trained": total_projections,
                "tensor_ratio": round(total_sent / max(1, len(self.events)), 3) if self.events else 0,
            },
            "agents": [{
                "name": a.name, "class": a.agent_class,
                "model": a.model_family,
                "context": a.context_class, "tokens": round(a.tokens),
                "perplexity": round(a.perplexity, 1),
                "lazarus_echoes": len(a.lazarus_echoes),
                "fragments_claimed": len(a.claimed_fragments),
                "tensor_sent": a.tensor_sent,
                "tensor_received": a.tensor_received,
                "concepts_owned": len(a.owned_concepts),
                "projections": len(a.trained_projections),
                "alive": a.alive, "cause": a.death_cause if not a.alive else "",
            } for a in sorted(agents.values(), key=lambda x: -x.tokens)],
            "actions": dict(actions.most_common(20)),
        }

        with open(os.path.join(self.out, "final_report.json"), "w") as f:
            json.dump(summary, f, indent=2)

        # Human-readable
        lines = [
            "# DeepWorld v4 — Tensor-Native Cognosphere",
            f"**Alive:** {summary['final']['alive']}/{len(agents)} | "
            f"**Lazarus:** {summary['final']['lazarus_agents']} | "
            f"**Tensors:** {summary['final']['tensor_sent']}s/{summary['final']['tensor_received']}r",
            f"**Context:** {summary['final']['context_distribution']}",
            f"**Models:** {summary['final']['model_distribution']}",
            f"**Concepts:** {summary['final']['concepts_owned']} | "
            f"**Projections:** {summary['final']['projections_trained']}",
            f"**Avg Perplexity:** {summary['final']['avg_perplexity']}",
            "",
            "## Agents",
            "| Name | Class | Model | Context | Tokens | Perp | Tensors s/r | Concepts | Proj | Status |",
            "|------|-------|-------|---------|--------|------|-------------|----------|------|--------|",
        ]
        for a in summary["agents"]:
            st = "DEAD" if not a["alive"] else ("👻" if a["lazarus_echoes"] else "OK")
            lines.append(
                f"| {a['name']} | {a['class']} | {a['model']} | {a['context']} | "
                f"{a['tokens']:.0f} | {a['perplexity']:.0f} | "
                f"{a['tensor_sent']}/{a['tensor_received']} | "
                f"{a['concepts_owned']} | {a['projections']} | {st} |"
            )
        lines += ["", "## Actions"]
        for act, cnt in summary["actions"].items():
            lines.append(f"- {act}: {cnt}")
        
        lines += ["", "## Tensor Actions"]
        tensor_actions = {k: v for k, v in summary["actions"].items() 
                         if k in ["send_tensor", "receive_tensor", "blend_tensors",
                                   "mine_concept", "train_projection", "route_tensor"]}
        for act, cnt in sorted(tensor_actions.items()):
            lines.append(f"- {act}: {cnt}")

        with open(os.path.join(self.out, "final_report.md"), "w") as f:
            f.write("\n".join(lines))
        return summary

    def close(self):
        self.tf.close()
