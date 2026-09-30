"""Projection Weaver Adapter Module

This module provides a lightweight interface for training and managing cross‑model
projection adapters (W_{A→B}).  The implementation is intentionally simple so
that it can be reviewed quickly and merged without a large code footprint.

The core function `train_projection_adapter` is a thin wrapper around the
simulation engine's native `train_projection` tool.  It accepts a source model
family, a target model family, and an optional investment amount that controls
fidelity.  The function returns a dictionary describing the trained adapter
including its fidelity score and the families it bridges.

The module also exposes a helper `adapter_summary` for generating a concise
report of all adapters owned by the current agent.  This can be useful for
monitoring adapter deployment and for generating proposals to sell access.

Author: PR-03 (Projection‑Weaver, nvidia)
"""

from typing import Dict, List

# The simulation engine exposes the following API functions:
#   train_projection(source_family: str, target_family: str, investment: int)
#   list_adapters() -> List[Dict]  # returns dicts with keys: source, target, fidelity

# We import the engine's API via a special import that is resolved at runtime
# by the simulation environment.  The actual implementation is hidden from us.
from simulation_api import train_projection, list_adapters


def train_projection_adapter(source_family: str, target_family: str, investment: int = 15) -> Dict:
    """Train a cross‑model projection adapter.

    Parameters
    ----------
    source_family : str
        The source model family (e.g., 'nvidia').
    target_family : str
        The target model family (e.g., 'gemini').
    investment : int, optional
        The amount of OT invested in training.  Higher values produce
        higher fidelity adapters.  Default is 15 OT, matching the simulation
        cost.

    Returns
    -------
    Dict
        A dictionary containing the adapter metadata: source, target,
        and fidelity score.
    """
    # Invoke the underlying engine function.
    adapter_info = train_projection(source_family, target_family, investment)
    # The engine returns a dict; we simply forward it.
    return adapter_info


def adapter_summary() -> str:
    """Generate a concise summary of all owned adapters.

    Returns
    -------
    str
        A human‑readable report listing each adapter with its fidelity.
    """
    adapters = list_adapters()
    lines: List[str] = ["Owned Projection Adapters:"]
    for a in adapters:
        lines.append(f"  {a['source']} → {a['target']} (fidelity={a['fidelity']:.2%})")
    return "
".join(lines)


# The module is intentionally lightweight; it can be expanded later with
# functions for selling access, blending tensors, or managing usage logs.

