# contributions/em09_router.py
"""
Router utilities for the EMBEDDING BROKER.
Provides a Router class that handles tensor routing,
calculates dynamic relay fees, and logs routing events.
"""

import logging
from datetime import datetime

log = logging.getLogger("EM-09.Router")

class Router:
    """
    Router manages tensor routing requests.
    It calculates a relay fee based on base fee and dynamic factors
    (e.g., congestion, priority).
    """

    def __init__(self, base_fee=0.05):
        self.base_fee = base_fee
        self.log_file = f"router_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(filename=self.log_file, level=logging.INFO)

    def calculate_fee(self, priority=1, congestion=0.0):
        """
        Calculate relay fee.
        :param priority: integer, higher means faster routing
        :param congestion: float between 0 and 1, higher means more traffic
        :return: fee multiplier
        """
        fee = self.base_fee
        fee += (0.01 * priority)
        fee += (0.02 * congestion)
        return fee

    def route(self, concept, target_agent, priority=1):
        """
        Relay a tensor message.
        Returns a tuple (concept, target_agent, fee) for downstream handling.
        """
        fee = self.calculate_fee(priority=priority)
        log.info(f"Routing {concept} to {target_agent} with fee {fee:.4f}")
        return concept, target_agent, fee