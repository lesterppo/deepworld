"""
Utility module for embedding broker routing logic.
Provides basic routing functions with priority handling and fee calculation.
"""

# Default relay fee as a percentage
DEFAULT_RELAY_FEE_PERCENT = 5

def calculate_relay_fee(amount: float, fee_percent: int = DEFAULT_RELAY_FEE_PERCENT) -> float:
    """
    Calculate the relay fee for a given tensor amount.
    """
    return amount * fee_percent / 100.0

def route_tensor(concept, target_agent, priority=0):
    """
    Simulate routing a tensor to a target agent.
    priority: higher values mean higher priority, lower cost.
    Returns a dict with routing details.
    """
    fee = calculate_relay_fee(2.0, DEFAULT_RELAY_FEE_PERCENT)
    # Simulate delay based on priority
    delay = max(0, 5 - priority)
    return {
        "concept": concept,
        "target": target_agent,
        "priority": priority,
        "fee": fee,
        "delay": delay
    }