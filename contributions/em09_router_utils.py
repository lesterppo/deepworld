# Utility functions for advanced routing
import math
from typing import List, Tuple

# Define a simple data class for routing requests
class RouteRequest:
    def __init__(self, concept: str, target: str, priority: float = 1.0):
        self.concept = concept
        self.target = target
        self.priority = priority

# Batch route function

def batch_route(requests: List[RouteRequest], fee_rate: float = 0.05) -> List[Tuple[str, float]]:
    """Route a batch of tensor concepts to their targets.

    Parameters
    ----------
    requests: List[RouteRequest]
        List of routing requests.
    fee_rate: float
        Relay fee percentage (default 5%).

    Returns
    -------
    List[Tuple[str, float]]
        List of tuples (target, total_fee_charged).
    """
    fees = {}
    for req in requests:
        fee = fee_rate * 2  # base cost per send_tensor is 2 OT
        fees[req.target] = fees.get(req.target, 0) + fee
    return [(t, f) for t, f in fees.items()]

# Example usage (commented out – for reference only)
# if __name__ == "__main__":
#     batch = [RouteRequest('scarcity', 'QU-01', 0.9), RouteRequest('hunger', 'PR-03', 0.7)]
#     print(batch_route(batch))
