# Routing utilities for the CMTIP bus
import logging

def log_route(concept, target_agent, priority):
    """Log routing information before calling route_tensor.
    This wrapper adds a debug log entry and then forwards the call to the
    broker's native route_tensor function. It helps operators trace traffic
    without modifying the core engine.
    """
    logging.info(f"Routing concept '{concept}' to '{target_agent}' with priority {priority}")
    # Call the broker's route_tensor function (assumed to be in scope)
    return route_tensor(concept, target_agent, priority)
