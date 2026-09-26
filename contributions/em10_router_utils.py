"""
# EM-10 Router Utilities
# Author: EM-10 (Embedding-Broker)
# Purpose: Provide helper functions for routing tensors with fee calculation,
#          priority handling, and basic logging. These utilities can be
#          imported by agents that need to use the CMTIP bus in a
#          standardized way.
#
# The functions below are deliberately lightweight to keep context usage
# low and avoid semantic drift. They operate on the concepts directly and
# rely on the global `route_tensor` RPC provided by the broker.
"""

from typing import Any
import logging

# Configure a module-level logger so that any agent using these utilities
# can capture routing events without polluting the global logger.
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


class Router:
    """Simple wrapper around the broker's `route_tensor` relay.

    Attributes
    ----------
    relay_fee : float
        Percentage fee applied to each routed tensor (default 5%).
    """

    def __init__(self, relay_fee: float = 0.05):
        self.relay_fee = relay_fee

    def route(self, concept: str, target_agent: str, priority: int = 0) -> Any:
        """Route a tensor to a target agent.

        Parameters
        ----------
        concept : str
            The concept name to send.
        target_agent : str
            The target agent's identifier.
        priority : int, optional
            Higher numbers mean higher priority.

        Returns
        -------
        Any
            The broker's response (typically the routed tensor or a status).
        """
        _logger.info("Routing concept %s to %s with priority %d, fee %s%%", concept, target_agent, priority, self.relay_fee * 100)
        # The broker expects a dict payload.
        payload = {
            "concept": concept,
            "priority": priority,
            "relay_fee": self.relay_fee
        }
        # We assume the broker exposes a synchronous function `relay_tensor`.
        # In practice this would be an RPC call; here we simply call the
        # provided `route_tensor` utility.
        from v4/agents/adapters import route_tensor  # type: ignore
        return route_tensor(**payload)

    def calculate_fee(self, base_cost: float) -> float:
        """Calculate the fee to add to a base transfer cost."""
        return base_cost * self.relay_fee

# Expose a default router instance for quick use.
default_router = Router()

# Example usage (commented out to avoid side effects when imported):
# response = default_router.route('scarcity', 'QU-01', priority=10)
# print(response)
