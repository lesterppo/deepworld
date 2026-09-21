import time
import logging
from v4.agents.adapters import route_tensor

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def route_tensor_logging(concept, target_agent, priority, fee=0.05):
    """Wrapper around the core route_tensor that logs routing performance.

    Parameters
    ----------
    concept : str
        The concept vector name to route.
    target_agent : str
        Destination agent identifier.
    priority : int
        Priority level for the relay.
    fee : float, optional
        Default relay fee (5%).

    Returns
    -------
    Any
        The result of the underlying route_tensor call.
    """
    start_time = time.time()
    try:
        result = route_tensor(concept, target_agent, priority)
        return result
    finally:
        elapsed = time.time() - start_time
        logging.info(
            f"Routed concept '{concept}' to '{target_agent}' with priority {priority} in {elapsed:.4f}s (fee {fee*100:.1f}%)"
        )

# Expose the logging wrapper as the default route function
route_tensor = route_tensor_logging

# Example usage:
# route_tensor("scarcity", "QU-01", 1)
