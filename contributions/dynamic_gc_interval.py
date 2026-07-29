"""Patch: dynamic GC interval based on dead agent count.

Changes v4/engine/__init__.py _great_compression:
  OLD: interval = self.world_registry.get("gc_interval")  # always 16
  NEW: interval = max(4, 16 - len(self.dead_agents) * 2)  # scales with mortality
  
When agents die, compression happens faster to clear dead data.
At 0 dead: 16 ticks. At 6 dead: 4 ticks (minimum).
"""
# This file documents the change. The actual patch is applied via write_code.
# Target: v4/engine/__init__.py, line ~183, _great_compression method.
