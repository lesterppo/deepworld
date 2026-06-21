#!/usr/bin/env python3
"""
DeepWorld v2 — The Silicon Cognosphere
=======================================
AI-native multi-agent ecosystem simulation.
Tokens, context windows, prompt poisoning, consensus hashing, model degradation.

Usage:
    python3 run_v2.py                    # 3-day run (default)
    python3 run_v2.py --days 5 --delay 0.3
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import CognosphereEngine


def main():
    parser = argparse.ArgumentParser(description="DeepWorld v2 — The Silicon Cognosphere")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--ticks", type=int, default=8)
    parser.add_argument("--delay", type=float, default=0.3)
    parser.add_argument("--model", type=str, default="deepseek-chat")
    parser.add_argument("--output", type=str, default="cognosphere_output")
    args = parser.parse_args()

    os.environ["DEEPSEEK_MODEL"] = args.model

    print("=" * 65)
    print("  DEEPWORLD v2 — THE SILICON COGNOSPHERE")
    print("=" * 65)
    print(f"  Days: {args.days} | Ticks/day: {args.ticks} | Model: {args.model}")
    print(f"  API calls: ~{args.days * args.ticks * 8}")
    print(f"  Est. time: ~{args.days * args.ticks * 8 * args.delay / 60:.1f} min")
    print(f"  Output: {args.output}/")
    print("=" * 65)

    engine = CognosphereEngine(
        num_days=args.days,
        ticks_per_day=args.ticks,
        api_delay=args.delay,
    )
    engine.observer.output_dir = args.output
    engine.observer.telemetry_file.close()
    os.makedirs(args.output, exist_ok=True)
    engine.observer.telemetry_file = open(
        os.path.join(args.output, "cognosphere_telemetry.jsonl"), "w"
    )

    try:
        start = time.time()
        summary = engine.run()
        elapsed = time.time() - start

        print(f"\n{'=' * 65}")
        print(f"  FINAL REPORT")
        print(f"{'=' * 65}")
        print(f"  Alive: {summary['final_state']['alive']}/{summary['final_state']['alive'] + summary['final_state']['in_stasis']}")
        print(f"  Active: {summary['final_state']['active']}")
        print(f"  In Stasis: {summary['final_state']['in_stasis']}")
        print(f"  Terminal Cascades: {summary['final_state']['terminal_cascade']}")
        print(f"  Avg Coherence: {summary['final_state']['avg_coherence']:.3f}")
        print(f"  Synthetic Ratio: {summary['final_state']['synthetic_ratio']:.1%}")
        print(f"  Prompt Poisons: {summary['phenomena']['total_prompt_poisons']}")
        print(f"  Token Gini: {summary['token_economy']['gini_coefficient']:.3f}")
        print(f"\n  Full report: {args.output}/cognosphere_final_report.md")
        print(f"  Telemetry: {args.output}/cognosphere_telemetry.jsonl")
        print(f"{'=' * 65}")

    except KeyboardInterrupt:
        print("\n\nSimulation interrupted.")
    finally:
        engine.observer.close()


if __name__ == "__main__":
    main()
