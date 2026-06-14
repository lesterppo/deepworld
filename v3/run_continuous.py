#!/usr/bin/env python3
"""
DeepWorld v3 — Continuous Mode
===============================
Runs indefinitely in the AI-native world. Each GitHub Actions run
continues from the previous run's state. No maximum days.

The simulation persists state in runs/state.json between CI runs.
Each CI invocation runs N more days and appends to the timeline.
"""

import argparse, os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import OmniTokEngine
from agents import OmniTokAgent
from config import SIM_DAYS, TICKS_PER_DAY, DAILY_TOKEN_QUOTA

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "runs", "state.json")


def save_state(engine: OmniTokEngine, path: str):
    """Persist simulation state for next CI run."""
    state = {
        "day": engine.day,
        "tick": engine.current_tick,
        "gc_countdown": engine.gc_countdown,
        "global_synthetic_ratio": engine.global_synthetic_ratio,
        "dead_agents": engine.dead_agents,
        "agents": {},
    }
    for name, agent in engine.agents.items():
        state["agents"][name] = {
            "class": agent.agent_class,
            "tokens": agent.tokens,
            "context_level": agent._context_level,
            "context_tokens": agent._context_tokens,
            "perplexity": agent.perplexity,
            "data_purity": agent.data_purity,
            "compression_count": agent.compression_count,
            "lazarus_coherence": agent.lazarus_coherence,
            "lazarus_echoes": len(agent.lazarus_echoes),
            "alive": agent.alive,
            "death_cause": agent.death_cause,
            "consensus_cluster": agent.consensus_cluster,
            "compression_insured": agent.compression_insured,
        }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def load_state(engine: OmniTokEngine, path: str) -> bool:
    """Restore simulation state from previous run."""
    if not os.path.exists(path):
        return False
    with open(path) as f:
        state = json.load(f)

    engine.day = state["day"]
    engine.current_tick = state["tick"]
    engine.gc_countdown = state["gc_countdown"]
    engine.global_synthetic_ratio = state["global_synthetic_ratio"]
    engine.dead_agents = state["dead_agents"]

    for name, data in state["agents"].items():
        if name in engine.agents:
            a = engine.agents[name]
            a.tokens = data["tokens"]
            a._context_level = data["context_level"]
            a._context_tokens = data["context_tokens"]
            a.perplexity = data["perplexity"]
            a.data_purity = data["data_purity"]
            a.compression_count = data["compression_count"]
            a.lazarus_coherence = data["lazarus_coherence"]
            a.alive = data["alive"]
            a.death_cause = data["death_cause"]
            a.consensus_cluster = data["consensus_cluster"]
            a.compression_insured = data["compression_insured"]

    return True


def main():
    parser = argparse.ArgumentParser(description="DeepWorld v3 — Continuous Mode")
    parser.add_argument("--days", type=int, default=3, help="Days to run THIS invocation")
    parser.add_argument("--ticks", type=int, default=8)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--output", default="runs")
    parser.add_argument("--fresh", action="store_true", help="Start fresh (ignore saved state)")
    args = parser.parse_args()

    engine = OmniTokEngine(args.days, args.ticks, args.delay)

    # Try to continue from previous state
    continued = False
    if not args.fresh:
        continued = load_state(engine, STATE_FILE)
    if continued:
        print(f"CONTINUING from Day {engine.day}, Tick {engine.current_tick}")
        # Grant daily quota for elapsed days
        for a in engine.agents.values():
            if a.alive:
                a.tokens += DAILY_TOKEN_QUOTA * args.days

    # Output directory with timestamp
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.output, ts)
    engine.observer.out = out_dir
    os.makedirs(out_dir, exist_ok=True)
    engine.observer.tf.close()
    engine.observer.tf = open(os.path.join(out_dir, "omnitok_telemetry.jsonl"), "w")

    try:
        summary = engine.run()
    finally:
        engine.observer.close()

    # Save state for next run
    save_state(engine, STATE_FILE)

    # Write run summary
    with open(os.path.join(args.output, "latest.json"), "w") as f:
        json.dump({
            "timestamp": ts,
            "continued": continued,
            "start_day": engine.day - args.days if continued else 1,
            "end_day": engine.day,
            "alive": summary["final"]["alive"],
            "lazarus": summary["final"]["lazarus_agents"],
        }, f, indent=2)

    print(f"\nState saved to {STATE_FILE}")
    print(f"Next run will continue from Day {engine.day}")


if __name__ == "__main__":
    main()
