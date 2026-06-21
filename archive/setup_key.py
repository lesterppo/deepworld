#!/usr/bin/env python3
"""Set up DeepWorld environment — enter your DeepSeek API key."""
import os

env_path = os.path.expanduser("~/deepworld/.env")
print("Enter your DeepSeek API key (starts with sk-):")
key = input().strip()

if not key.startswith("sk-"):
    print("ERROR: Key should start with 'sk-'. Got:", key[:10] + "...")
    exit(1)

with open(env_path, "w") as f:
    f.write(f"DEEPSEEK_API_KEY={key}\n")
os.chmod(env_path, 0o600)
print(f"Key written to {env_path}")
print("Run: source ~/deepworld/.env && python3 run_simulation.py --days 5")
