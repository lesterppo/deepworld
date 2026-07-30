#!/usr/bin/env python3
"""Test all models in NVIDIA_FREE_MODELS against live API.
Usage: NVIDIA_API_KEY=... python3 scripts/test_models.py
Outputs CSV of working models for use in config."""
import os, re, sys, json
from openai import OpenAI

key = os.environ.get("NVIDIA_API_KEY")
if not key:
    print("Set NVIDIA_API_KEY env var", file=sys.stderr)
    sys.exit(1)

config = open("v4/config/__init__.py").read()
pool = re.findall(r'"([^"]+)"', config[config.index("NVIDIA_FREE_MODELS"):config.index("]", config.index("NVIDIA_FREE_MODELS"))])

client = OpenAI(api_key=key, base_url="https://integrate.api.nvidia.com/v1", timeout=15)
working, failing = [], {}

for m in pool:
    try:
        r = client.chat.completions.create(model=m, messages=[{"role":"user","content":"OK"}], max_tokens=5, temperature=0)
        c = r.choices[0].message.content or ""
        if c.strip():
            print(f"✅ {m}")
            working.append(m)
        else:
            print(f"❌ {m} — empty response")
            failing[m] = "empty"
    except Exception as e:
        print(f"❌ {m} — {type(e).__name__}")
        failing[m] = type(e).__name__

print(f"\n{len(working)}/{len(pool)} working")
print(json.dumps(working, indent=2))
