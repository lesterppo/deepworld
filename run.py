#!/usr/bin/env python3
"""
DeepWorld v5 — Tensor-Native Multi-Agent Cognosphere
=====================================================
Root entry point. Delegates to v4 engine.

Default mode: NVIDIA-only (DEEPWORLD_NVIDIA_ONLY=1)
All agents get random free models from NVIDIA NIM.

Usage:
  python3 run.py --days 3 --ticks 8                    # NVIDIA-only (default)
  python3 run.py --multi-model                          # All backends (needs keys)
  python3 run.py --days 5 --ticks 12 --output runs/     # CI mode
"""

import argparse, os, sys, time, json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "v4"))

from engine import OmniTokV4Engine


def health_check_nvidia() -> bool:
    """Verify NVIDIA API is reachable before starting simulation."""
    from openai import OpenAI
    import os

    api_key = os.environ.get("NVIDIA_API_KEY", "")
    if not api_key:
        env_path = os.path.expanduser("~/deepworld/.env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if "=" in line and line.startswith("NVIDIA_API_KEY"):
                        api_key = line.strip().split("=", 1)[1]
                        break

    if not api_key:
        print("\n[DEEPWORLD] ❌ NVIDIA_API_KEY not found!", file=sys.stderr)
        print("[DEEPWORLD] Set NVIDIA_API_KEY in ~/.hermes/.env or ~/deepworld/.env", file=sys.stderr)
        return False

    try:
        client = OpenAI(api_key=api_key, base_url="https://integrate.api.nvidia.com/v1")
        resp = client.chat.completions.create(
            model="nvidia/llama-3.1-nemotron-nano-8b-v1",
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5, temperature=0,
        )
        content = resp.choices[0].message.content or ""
        print(f"[DEEPWORLD] ✅ NVIDIA health check OK (response: '{content.strip()}')", file=sys.stderr)
        return True
    except Exception as e:
        print(f"\n[DEEPWORLD] ❌ NVIDIA health check FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False


def main():
    p = argparse.ArgumentParser(description="DeepWorld v5 — Tensor-Native Cognosphere")
    p.add_argument("--days", type=int, default=3, help="Simulation days (default: 3)")
    p.add_argument("--ticks", type=int, default=8, help="Ticks per day (default: 8)")
    p.add_argument("--delay", type=float, default=0.5, help="Delay between ticks in seconds")
    p.add_argument("--output", default="runs", help="Output directory")
    p.add_argument("--multi-model", action="store_true",
                   help="Use all backends (DeepSeek+Gemini+Claude+Nvidia) instead of NVIDIA-only")
    p.add_argument("--single-model", default="auto",
                   help="Use single model family (only with --multi-model)")
    p.add_argument("--no-cmtip", action="store_true", help="Disable tensor communication")
    p.add_argument("--no-health-check", action="store_true", help="Skip pre-flight health check")

    a = p.parse_args()

    # NVIDIA-only by default
    if not a.multi_model:
        os.environ["DEEPWORLD_NVIDIA_ONLY"] = "1"
        backend_label = "NVIDIA NIM (free, random models per agent)"
    else:
        os.environ["DEEPWORLD_NVIDIA_ONLY"] = "0"
        backend_label = "Multi-model (DeepSeek + Gemini + Claude + Nvidia)"

    # Health check
    if not a.no_health_check:
        if not health_check_nvidia():
            sys.exit(1)

    print(f"\n  DeepWorld v5 | {a.days}d × {a.ticks}t | "
          f"~{a.days * a.ticks * 10 * a.delay / 60:.1f}min | "
          f"CMTIP: {'OFF' if a.no_cmtip else 'ON'}")
    print(f"  Backend: {backend_label}")

    engine = OmniTokV4Engine(
        days=a.days, ticks_per_day=a.ticks, delay=a.delay,
        use_cmtip=not a.no_cmtip,
        single_model=a.single_model,
    )

    # Setup output
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(a.output, ts)
    os.makedirs(out_dir, exist_ok=True)

    engine.observer.out = out_dir
    engine.observer.tf.close()
    engine.observer.tf = open(os.path.join(out_dir, "omnitok_telemetry.jsonl"), "w")

    try:
        t0 = time.time()
        summary = engine.run()
        elapsed = time.time() - t0
        print(f"\n  Done in {elapsed:.0f}s. Report: {out_dir}/final_report.md")

        # Persist world state
        engine._save_registry()

        # ─── Resolve contribution proposals and apply to repo (v5.1) ───
        if engine.contribution_proposals:
            accepted_props = [p for p in engine.contribution_proposals if p["status"] == "accepted"]
            rejected_props = [p for p in engine.contribution_proposals if p["status"] == "rejected"]
            pending_props = [p for p in engine.contribution_proposals if p["status"] == "pending"]
            
            print(f"\n  📝 Contribution Governance:")
            print(f"     Accepted: {len(accepted_props)} | Rejected: {len(rejected_props)} | Pending: {len(pending_props)}")
            
            # Award acceptance bonuses
            for prop in accepted_props:
                proposer = prop["agent"]
                bonus = prop.get("accept_bonus", 300)
                if proposer in engine.agents:
                    engine.agents[proposer].tokens += bonus
                    engine.agents[proposer].tokens_earned += bonus
                # Mark staged files as committed
                for c in prop.get("staged", []):
                    c["committed"] = True
                    c["commit_agent"] = prop["agent"]
                    c["commit_message"] = prop["message"]
                print(f"     ✅ {prop['id']} by {proposer}: ACCEPTED +{bonus} OT bonus ({prop['files']} files)")
            
            for prop in rejected_props:
                print(f"     ❌ {prop['id']} by {prop['agent']}: REJECTED (initiator keeps 50 OT base)")
            
            # Write accepted files to disk
            accepted_files = []
            for prop in accepted_props:
                for c in prop.get("staged", []):
                    if c.get("action") in ("write_code", "document_code"):
                        accepted_files.append(c)
            
            if accepted_files:
                print(f"\n  📝 Writing {len(accepted_files)} accepted files...")
                repo_root = os.path.dirname(os.path.abspath(__file__))
                for c in accepted_files:
                    filepath = os.path.join(repo_root, c["filepath"])
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, "w") as f:
                        f.write(c["content"])
                    print(f"    ✓ {c['filepath']} (by {c['agent']})")
                
                manifest_path = os.path.join(out_dir, "contributions.json")
                with open(manifest_path, "w") as f:
                    json.dump([{
                        "agent": c["agent"], "agent_class": c.get("agent_class"),
                        "filepath": c["filepath"], "description": c.get("description", ""),
                        "action": c["action"], "reward": c.get("reward", 0),
                        "proposal_id": c.get("proposal_id", ""),
                    } for c in accepted_files], f, indent=2)
                print(f"    ✓ Files written. CI will commit.")

        # Governance events
        events = engine.world_registry.get_recent_events(5)
        if events:
            print(f"\n  Governance Events:")
            for e in events:
                print(f"    T{e.get('tick', '?')}: {e.get('event', '?')} — "
                      f"{e.get('param', '')} {e.get('old_value', '?')}→{e.get('new_value', '?')}")

        # Agent summary
        print(f"\n  Agent Summary:")
        for agent_info in summary["agents"]:
            alive_str = "✓" if agent_info["alive"] else "✗"
            short_model = agent_info.get("model", "?").split("/")[-1]
            rep = agent_info.get("dev_rep", 0)
            rep_str = f" 💻:{rep}" if rep > 0 else ""
            print(f"    {alive_str} {agent_info['name']} ({agent_info.get('class','?')}/{short_model}) "
                  f"OT={agent_info.get('tokens', 0):.0f}{rep_str}")

    except KeyboardInterrupt:
        print("\n  Interrupted.")
    finally:
        engine.observer.close()


if __name__ == "__main__":
    main()
