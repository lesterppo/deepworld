# contributions/em10_route_logger.py
"""
Utility module for Embedding Broker EM-10.
Provides logging functionality for tensor routing and metrics.
"""

import logging
from datetime import datetime

logger = logging.getLogger("em10_route_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def log_route(concept, target_agent, priority, fee):
    """Log routing details for a tensor message."""
    logger.info(f"Routing concept '{concept}' to agent '{target_agent}' "
                f"with priority {priority} and fee {fee:.2f} OT")