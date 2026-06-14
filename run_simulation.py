#!/usr/bin/env python3
"""
DeepWorld — Multi-Agent Sandbox Simulation
==========================================
Based on Emergence AI's "Emergent World" experiment.
Runs 10 DeepSeek-powered agents in a shared virtual town with
scarcity, democracy, crime, and emergent behavior.

Usage:
    python run_simulation.py                    # 5-day run (default)
    python run_simulation.py --days 15          # Full 15-day run
    python run_simulation.py --days 3 --delay 0.2 # Faster, shorter run
    python run_simulation.py --model deepseek-reasoner  # Use R1

Requirements:
    pip install openai pyyaml
    DEEPSEEK_API_KEY env var or ~/.hermes/config.yaml
"""

import argparse
import os
import sys
import time

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.sim_loop import DeepWorldEngine


def main():
    parser = argparse.ArgumentParser(
        description="DeepWorld — Multi-Agent Sandbox Simulation"
    )
    parser.add_argument(
        "--days", type=int, default=5,
        help="Number of simulation days (default: 5, original experiment: 15)"
    )
    parser.add_argument(
        "--ticks", type=int, default=12,
        help="Ticks per day (default: 12 = virtual hours)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.3,
        help="API call delay in seconds (default: 0.3, lower if rate limits allow)"
    )
    parser.add_argument(
        "--model", type=str, default="deepseek-chat",
        help="DeepSeek model to use (default: deepseek-chat, alt: deepseek-reasoner)"
    )
    parser.add_argument(
        "--output", type=str, default="simulation_output",
        help="Output directory for reports and telemetry"
    )
    args = parser.parse_args()

    # Set model globally
    os.environ["DEEPSEEK_MODEL"] = args.model

    print("=" * 60)
    print("  DEEPWORLD — Multi-Agent Sandbox Simulation")
    print("=" * 60)
    print(f"  Days:        {args.days}")
    print(f"  Ticks/day:   {args.ticks}")
    print(f"  Model:       {args.model}")
    print(f"  API delay:   {args.delay}s")
    print(f"  Output:      {args.output}/")
    print(f"  API calls:   ~{args.days * args.ticks * 10} (agent actions)")
    print(f"  Est. time:   ~{args.days * args.ticks * 10 * args.delay / 60:.1f} minutes")
    print("=" * 60)
    print()

    # Confirm
    if args.days >= 10:
        print(f"⚠  This will make ~{args.days * args.ticks * 10} API calls")
        print(f"   and take ~{args.days * args.ticks * 10 * args.delay / 60:.1f} minutes.")
        response = input("   Continue? [y/N]: ").strip().lower()
        if response != "y":
            print("Aborted.")
            return

    engine = DeepWorldEngine(
        num_days=args.days,
        ticks_per_day=args.ticks,
        api_delay=args.delay,
    )
    engine.observer.output_dir = args.output
    engine.observer.__init__(args.output)  # re-init with correct path
    # Re-open telemetry file
    engine.observer.telemetry_file.close()
    engine.observer.telemetry_file = open(
        os.path.join(args.output, "simulation_telemetry.jsonl"), "w"
    )

    try:
        start_time = time.time()
        summary = engine.run()
        elapsed = time.time() - start_time

        print(f"\n{'=' * 60}")
        print(f"  FINAL REPORT")
        print(f"{'=' * 60}")
        print(f"  Survivors: {summary['final_state']['alive']}/10")
        print(f"  Total crimes: {summary['statistics']['total_crimes']}")
        print(f"  Proposals passed: {summary['statistics']['proposals_passed']}")
        print(f"  Elapsed: {elapsed:.1f}s ({elapsed/60:.1f}m)")
        print(f"\n  Full report: {args.output}/final_report.md")
        print(f"  JSON telemetry: {args.output}/simulation_telemetry.jsonl")
        print(f"  Daily summaries: {args.output}/day_*.json")
        print(f"{'=' * 60}")

    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    finally:
        engine.cleanup()
        engine.observer.close()


if __name__ == "__main__":
    main()
