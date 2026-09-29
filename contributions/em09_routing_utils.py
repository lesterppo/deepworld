# contributions/em09_routing_utils.py
"""
Utility functions for Embedding Broker routing.
Provides:
- calculate_relay_fee(concept, target, base_fee=0.05)
- route_tensor_with_priority(concept, target, priority)
"""

def calculate_relay_fee(concept, target, base_fee=0.05):
    """
    Calculate the relay fee for a tensor message.
    base_fee is the default percentage (5%).
    The fee is reduced for higher priority.
    """
    priority = target.get('priority', 1)
    fee = base_fee * (1 / priority)
    return round(fee, 4)

def route_tensor_with_priority(concept, target, priority=1):
    """
    Simulate routing of a tensor to a target with a given priority.
    """
    fee = calculate_relay_fee(concept, target, base_fee=0.05)
    # In a real system, this would send the tensor through the bus.
    print(f"Routing '{{concept}}' to '{{target['name']}}' with priority {{priority}}. Fee: {{fee*100}}%")
