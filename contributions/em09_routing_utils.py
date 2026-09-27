"""
Utility functions for embedding broker routing.
"""

def calculate_relay_fee(amount, fee_percent=5):
    """Return the fee for a given amount and fee percentage.
    Default is 5% as per broker settings.
    """
    return amount * fee_percent / 100


def route_tensor(concept, target_agent, priority=1):
    """Stub for routing a tensor through the CMTIP bus.

    Parameters
    ----------
    concept : str
        The concept to be routed.
    target_agent : str
        Identifier of the target agent.
    priority : int, optional
        Routing priority; higher means faster.

    Returns
    -------
    dict
        Metadata about the routed tensor.
    """
    # Placeholder implementation – actual bus interaction will be handled elsewhere.
    fee = calculate_relay_fee(100)  # Example fee calculation
    return {
        "concept": concept,
        "target": target_agent,
        "priority": priority,
        "relay_fee": fee
    }
