#!/usr/bin/env python3
"""
DeepWorld v4 — Tensor-Native Multi-Model Ecosystem
====================================================
"Not humans pretending to be bots — AI agents navigating token economies,
context windows, embedding drift, and tensor communication."

Multi-model support: DeepSeek API (paid) + Gemini Web (free) + Claude Web (free)
CMTIP tensor bus: agents communicate via compressed embedding vectors

Usage:
  python3 run_v4.py --days 3 --ticks 8                    # all models (auto)
  python3 run_v4.py --single-model deepseek                # DeepSeek only
  python3 run_v4.py --single-model gemini_flash --free     # Gemini Flash only (free)
  python3 run_v4.py --no-cmtip                             # Text-only (v3 mode)
  python3 run_v4.py --days 5 --ticks 12 --delay 0.1        # Fast mode
"""

import argparse, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import OmniTokV4Engine


def main():
    p = argparse.ArgumentParser(description="DeepWorld v4 — Tensor-Native Cognosphere")
    p.add_argument("--days", type=int, default=3, help="Simulation days (default: 3)")
    p.add_argument("--ticks", type=int, default=8, help="Ticks per day (default: 8)")
    p.add_argument("--delay", type=float, default=0.5, help="Delay between ticks in seconds")
    p.add_argument("--output", default="omnitok_v4_output", help="Output directory")
    p.add_argument("--single-model", default="auto", 
                   help="Use single model: deepseek, gemini_flash, gemini_pro, claude, or auto")
    p.add_argument("--no-cmtip", action="store_true", help="Disable tensor communication (v3 text mode)")
    p.add_argument("--free", action="store_true", help="Free models only (Gemini web + Claude web)")
    
    a = p.parse_args()
    
    if a.free:
        os.environ["DEEPWORLD_FREE"] = "1"
        if a.single_model == "auto":
            a.single_model = "gemini_flash"
    
    print(f"\n  DeepWorld v4 | {a.days}d × {a.ticks}t | "
          f"~{a.days * a.ticks * 10 * a.delay / 60:.1f}min | "
          f"CMTIP: {'OFF' if a.no_cmtip else 'ON'}")
    
    engine = OmniTokV4Engine(
        days=a.days, ticks_per_day=a.ticks, delay=a.delay,
        use_cmtip=not a.no_cmtip,
        single_model=a.single_model,
    )
    
    # Setup output
    engine.observer.out = a.output
    engine.observer.tf.close()
    os.makedirs(a.output, exist_ok=True)
    engine.observer.tf = open(os.path.join(a.output, "omnitok_telemetry.jsonl"), "w")
    
    try:
        t0 = time.time()
        summary = engine.run()
        elapsed = time.time() - t0
        print(f"\n  Done in {elapsed:.0f}s. Report: {a.output}/final_report.md")
        
        # Persist world state for next run
        engine._save_registry()
        
        # Show governance events
        events = engine.world_registry.get_recent_events(5)
        if events:
            print(f"\n  Governance Events:")
            for e in events:
                print(f"    T{e.get('tick', '?')}: {e.get('event', '?')} — {e.get('param', '')} {e.get('old_value', '?')}→{e.get('new_value', '?')}")
        
        # Agent summary
        print(f"\n  Agent Summary:")
        for agent_info in summary["agents"]:
            alive_str = "✓" if agent_info["alive"] else "✗"
            print(f"    {alive_str} {agent_info['name']} ({agent_info['class']}/{agent_info['model']}) "
                  f"OT={agent_info['tokens']:.0f} ts={agent_info['tensor_sent']}/{agent_info['tensor_received']}")
        
    except KeyboardInterrupt:
        print("\n  Interrupted.")
    finally:
        engine.observer.close()


if __name__ == "__main__":
    main()
