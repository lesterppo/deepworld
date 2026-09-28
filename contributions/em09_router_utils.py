def route_tensor_with_priority(concept, target_agent, priority):
    """Route a tensor with priority handling.
    Priority determines the fee multiplier and ordering.
    """
    base_fee = 3  # base relay fee in OT
    fee_multiplier = 1 + (priority / 10)  # priority 1-10 scales fee
    fee = base_fee * fee_multiplier
    # Simulate routing logic: log and return fee
    print(f"Routing {concept} to {target_agent} with priority {priority}, fee {fee:.2f} OT")
    return fee
