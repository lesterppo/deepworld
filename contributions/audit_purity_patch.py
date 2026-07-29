"""Patch: audit_consistency success rate scales with data_purity.

Apply this diff to v4/agents/__init__.py:
  OLD: if random.random() < 0.3:
                bounty = random.randint(20, 60)
  NEW: # Audit success scales with data_purity (15% base + purity*40%)
                if random.random() < 0.15 + self.data_purity * 0.4:
                    bounty = random.randint(25, 70)  # Higher bounties for purity-based audits

Reason: Loss-Miner audit success should reflect agent data quality.
Agents with high purity (>0.8) get ~47% audit success instead of flat 30%.
"""
# This file documents the change. The actual engine patch comes via the
# write_code args which the engine dispatcher applies.
