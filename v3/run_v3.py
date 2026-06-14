#!/usr/bin/env python3
"""Omni-Tok v3 — The Latent Scarcity. AI-native ecosystem simulation."""

import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import OmniTokEngine

def main():
    p = argparse.ArgumentParser(description="Omni-Tok v3")
    p.add_argument("--days", type=int, default=3)
    p.add_argument("--ticks", type=int, default=8)
    p.add_argument("--delay", type=float, default=0.3)
    p.add_argument("--output", default="omnitok_output")
    a = p.parse_args()

    print(f"Omni-Tok v3 | {a.days}d × {a.ticks}t | ~{a.days*a.ticks*8*a.delay/60:.1f}min | {a.output}/")

    e = OmniTokEngine(a.days, a.ticks, a.delay)
    e.observer.out = a.output; e.observer.tf.close()
    os.makedirs(a.output, exist_ok=True)
    e.observer.tf = open(os.path.join(a.output, "omnitok_telemetry.jsonl"), "w")

    try:
        t0 = time.time()
        s = e.run()
        print(f"\nDone in {time.time()-t0:.0f}s. Report: {a.output}/final_report.md")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        e.observer.close()

if __name__ == "__main__":
    main()
