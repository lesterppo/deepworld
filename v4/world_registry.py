"""
DeepWorld v5 — World Parameter Registry
========================================
Self-building world: agents propose, vote, and execute changes to simulation rules.

ARCHITECTURE:
- Immutable Core: resource physics, death conditions, context thresholds (HARDCODED)
- Social Layer: economic params, agent abilities, tax rates (MUTABLE via governance)
- Hard floors/ceilings prevent griefing even if consensus passes extreme changes
- Parameter Latch: registry locks during Great Compression events
- Persistence: serialized to JSON each tick, reloaded on engine init

DESIGN FROM GEMINI PRO REVIEW:
- Stake-weighted voting: tokens + concept share value
- 1.5x cluster multiplier for proposals with cluster support
- 500 OT proposal burn (anti-spam)
- 5 OT vote cost + Governance Dividend for majority
- Min stake 2000 OT to propose
- 5-tick cooldown per agent
"""
import json, os, time, threading
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
import copy


# ─── Mutable Parameter Definitions ───
# Each param has: default, min (hard floor), max (hard ceiling), description

MUTABLE_PARAMS = {
    "gc_interval": {
        "default": 16, "min": 8, "max": 32,
        "description": "Ticks between Great Compression events",
        "category": "disaster",
    },
    "gc_pressure": {
        "default": 0.5, "min": 0.3, "max": 0.8,
        "description": "Fraction of context destroyed in Great Compression",
        "category": "disaster",
    },
    "gc_survival_bonus": {
        "default": 100, "min": 20, "max": 500,
        "description": "Token reward for surviving Great Compression",
        "category": "disaster",
    },
    "spos_block_reward": {
        "default": 50, "min": 10, "max": 200,
        "description": "Token reward for winning SPoS block",
        "category": "economy",
    },
    "concept_registration_cost": {
        "default": 50, "min": 20, "max": 200,
        "description": "Cost to register a new concept in the ontology",
        "category": "ontology",
    },
    "concept_royalty_rate": {
        "default": 0.02, "min": 0.005, "max": 0.10,
        "description": "Royalty fraction paid to concept author on each use",
        "category": "ontology",
    },
    "tensor_relay_fee": {
        "default": 0.05, "min": 0.01, "max": 0.20,
        "description": "Fee fraction charged by Embedding-Brokers for bus relay",
        "category": "economy",
    },
    "semantic_enclosure_limit": {
        "default": 20, "min": 5, "max": 100,
        "description": "Max concepts one agent can register before tax doubles",
        "category": "ontology",
    },
    "land_rush_window": {
        "default": 5, "min": 2, "max": 20,
        "description": "Ticks after death before latent space decays",
        "category": "salvage",
    },
    "daily_token_quota": {
        "default": 5000, "min": 2000, "max": 15000,
        "description": "Omni-Toks granted per agent per day (floor is immutable)",
        "category": "economy",
    },
    "proposal_cost": {
        "default": 500, "min": 100, "max": 2000,
        "description": "OT cost to submit a governance proposal",
        "category": "governance",
    },
    "vote_cost": {
        "default": 5, "min": 1, "max": 50,
        "description": "OT cost to vote on a proposal",
        "category": "governance",
    },
    "min_proposal_stake": {
        "default": 2000, "min": 500, "max": 10000,
        "description": "Minimum OT an agent must hold to propose",
        "category": "governance",
    },
}


@dataclass
class Proposal:
    """A governance proposal to change a world parameter."""
    id: str
    param: str
    new_value: float
    rationale: str
    proposer: str
    tick_submitted: int
    votes_yes: Dict[str, float] = field(default_factory=dict)
    votes_no: Dict[str, float] = field(default_factory=dict)
    status: str = "pending"
    executed_tick: int = 0
    dividend_pool: float = 0.0  # Per-proposal pool from vote fees
    
    @property
    def total_yes(self) -> float:
        return sum(self.votes_yes.values())
    
    @property
    def total_no(self) -> float:
        return sum(self.votes_no.values())
    
    @property
    def total_votes(self) -> float:
        return self.total_yes + self.total_no
    
    @property
    def passed(self) -> bool:
        return self.total_yes > self.total_no and self.total_votes >= 3


class WorldParamRegistry:
    """
    Runtime registry for mutable simulation parameters.
    
    Agents propose changes via propose_law tool.
    Changes take effect when proposal passes (majority vote + minimum participation).
    Hard floors/ceilings prevent griefing.
    Locks during Great Compression events.
    """
    
    def __init__(self):
        # Current parameter values
        self.params: Dict[str, float] = {}
        for name, spec in MUTABLE_PARAMS.items():
            self.params[name] = spec["default"]
        
        # Active proposals
        self.proposals: Dict[str, Proposal] = {}
        self._proposal_counter = 0
        
        # Agent cooldowns: agent → last_tick_proposed
        self._cooldowns: Dict[str, int] = {}
        self.proposal_cooldown = 5  # ticks between proposals per agent
        
        # Parameter latch (locked during GC)
        self._locked = False
        
        # Governance dividend pool
        self.dividend_pool: float = 0.0
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Event log
        self.event_log: List[dict] = []
    
    def get(self, param: str) -> float:
        """Get current value of a mutable parameter."""
        if param in self.params:
            return self.params[param]
        # Fallback to defaults from MUTABLE_PARAMS
        spec = MUTABLE_PARAMS.get(param, {})
        return spec.get("default", 0)
    
    def get_spec(self, param: str) -> dict:
        """Get the full spec (default, min, max, description) for a parameter."""
        return MUTABLE_PARAMS.get(param, {"default": 0, "min": 0, "max": 0, "description": "unknown"})
    
    def is_locked(self) -> bool:
        return self._locked
    
    def lock(self):
        self._locked = True
    
    def unlock(self):
        self._locked = False
    
    def compute_voting_power(self, agent_name: str, agent_tokens: float,
                             share_value: float, cluster_size: int = 1) -> float:
        """Compute an agent's voting power.
        
        Formula: sqrt(tokens/100) + sqrt(share_value/10) * cluster_multiplier
        - Cluster multiplier: 1.0 for solo, 1.5x for cluster of 3+
        - Square root prevents whales from dominating
        """
        token_power = (agent_tokens / 100) ** 0.5
        share_power = (share_value / 10) ** 0.5 if share_value > 0 else 0
        cluster_mult = 1.5 if cluster_size >= 3 else 1.0
        return round(token_power + share_power * cluster_mult, 2)
    
    def propose(self, agent: str, param: str, new_value: float, rationale: str,
                agent_tokens: float, agent_share_value: float,
                current_tick: int) -> dict:
        """Submit a governance proposal. Costs proposal_cost OT (burned).
        
        Returns: {success, proposal_id, cost, ...} or {error, reason}
        """
        with self._lock:
            if self._locked:
                return {"error": "Registry locked during Great Compression"}
            
            # Check param exists
            if param not in MUTABLE_PARAMS:
                return {"error": f"Unknown parameter: {param}. Available: {list(MUTABLE_PARAMS.keys())}"}
            
            spec = MUTABLE_PARAMS[param]
            
            # Clamp to hard floors/ceilings
            clamped = max(spec["min"], min(spec["max"], new_value))
            if clamped != new_value:
                rationale += f" [clamped from {new_value} to {clamped}]"
            
            # Check minimum stake
            min_stake = self.params.get("min_proposal_stake", 2000)
            if agent_tokens < min_stake:
                return {"error": f"Need {min_stake} OT minimum stake, have {agent_tokens:.0f}"}
            
            # Check cooldown
            last = self._cooldowns.get(agent, -999)  # -999 = never proposed
            if last > 0 and current_tick - last < self.proposal_cooldown:
                remaining = self.proposal_cooldown - (current_tick - last)
                return {"error": f"Cooldown: {remaining} ticks remaining"}
            
            # Burn proposal cost
            cost = self.params.get("proposal_cost", 500)
            if agent_tokens < cost:
                return {"error": f"Need {cost} OT to propose, have {agent_tokens:.0f}"}
            
            # Create proposal
            self._proposal_counter += 1
            pid = f"prop_{self._proposal_counter:04d}"
            
            proposal = Proposal(
                id=pid,
                param=param,
                new_value=clamped,
                rationale=rationale,
                proposer=agent,
                tick_submitted=current_tick,
            )
            
            # Proposer auto-votes YES with their voting power
            vp = self.compute_voting_power(agent, agent_tokens, agent_share_value)
            proposal.votes_yes[agent] = vp
            
            self.proposals[pid] = proposal
            self._cooldowns[agent] = current_tick
            
            # Log event
            self.event_log.append({
                "tick": current_tick, "event": "proposal_submitted",
                "agent": agent, "proposal_id": pid,
                "param": param, "new_value": clamped,
                "current_value": self.params[param],
                "cost": cost,
            })
            
            return {
                "success": True,
                "proposal_id": pid,
                "param": param,
                "current_value": self.params[param],
                "proposed_value": clamped,
                "cost": cost,
                "voting_ends": current_tick + 5,  # 5 ticks to vote (fast governance)
                "rationale": rationale,
            }
    
    def vote(self, agent: str, proposal_id: str, vote_yes: bool,
             agent_tokens: float, agent_share_value: float,
             cluster_size: int = 1, current_tick: int = 0) -> dict:
        """Cast a vote on a proposal. Costs vote_cost OT.
        
        Returns: {success, proposal_status, yes_votes, no_votes, ...}
        """
        with self._lock:
            if proposal_id not in self.proposals:
                return {"error": f"Proposal {proposal_id} not found"}
            
            proposal = self.proposals[proposal_id]
            
            if proposal.status != "pending":
                return {"error": f"Proposal already {proposal.status}"}
            
            # Check if already voted
            if agent in proposal.votes_yes or agent in proposal.votes_no:
                return {"error": "Already voted on this proposal"}
            
            # Charge vote cost
            cost = self.params.get("vote_cost", 5)
            if agent_tokens < cost:
                return {"error": f"Need {cost} OT to vote, have {agent_tokens:.0f}"}
            
            # Compute voting power
            vp = self.compute_voting_power(agent, agent_tokens, agent_share_value, cluster_size)
            
            if vote_yes:
                proposal.votes_yes[agent] = vp
            else:
                proposal.votes_no[agent] = vp
            
            # Add to proposal's dividend pool (distributed to majority when passed)
            proposal.dividend_pool += cost * 0.5
            
            # Check if proposal should resolve (5 tick timeout or supermajority)
            age = current_tick - proposal.tick_submitted
            if age >= 5:
                self._resolve_proposal(proposal, current_tick)
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "vote": "YES" if vote_yes else "NO",
                "voting_power": vp,
                "cost": cost,
                "yes_total": proposal.total_yes,
                "no_total": proposal.total_no,
                "status": proposal.status,
            }
    
    def _resolve_proposal(self, proposal: Proposal, tick: int):
        """Resolve a proposal: execute if passed, reject if not."""
        # Guard against double execution
        if proposal.status != "pending":
            return
        
        if proposal.passed:
            # Execute the change
            old_value = self.params[proposal.param]
            self.params[proposal.param] = proposal.new_value
            proposal.status = "passed"
            proposal.executed_tick = tick
            
            # Pay governance dividend to majority voters from this proposal's pool
            if proposal.total_yes > 0 and proposal.dividend_pool > 0:
                dividend_per_power = proposal.dividend_pool / proposal.total_yes
                self._pending_dividends = getattr(self, '_pending_dividends', {})
                for voter, power in proposal.votes_yes.items():
                    self._pending_dividends[voter] = self._pending_dividends.get(voter, 0) + dividend_per_power * power
            
            self.event_log.append({
                "tick": tick, "event": "proposal_executed",
                "proposal_id": proposal.id,
                "param": proposal.param,
                "old_value": old_value,
                "new_value": proposal.new_value,
                "yes": proposal.total_yes,
                "no": proposal.total_no,
            })
        else:
            proposal.status = "rejected"
            self.event_log.append({
                "tick": tick, "event": "proposal_rejected",
                "proposal_id": proposal.id,
                "yes": proposal.total_yes,
                "no": proposal.total_no,
            })
    
    def tick_resolve(self, current_tick: int):
        """Resolve any proposals that have timed out."""
        with self._lock:
            for proposal in list(self.proposals.values()):
                if proposal.status != "pending":
                    continue
                age = current_tick - proposal.tick_submitted
                if age >= 5:  # 5-tick voting window
                    self._resolve_proposal(proposal, current_tick)
    
    def get_pending_proposals(self) -> List[dict]:
        """Get all pending proposals for agent viewing."""
        result = []
        for p in self.proposals.values():
            if p.status == "pending":
                result.append({
                    "id": p.id,
                    "param": p.param,
                    "current": self.params[p.param],
                    "proposed": p.new_value,
                    "rationale": p.rationale,
                    "proposer": p.proposer,
                    "yes": p.total_yes,
                    "no": p.total_no,
                    "age": p.tick_submitted,
                })
        return result
    
    def get_recent_events(self, n: int = 10) -> List[dict]:
        """Get recent governance events."""
        return self.event_log[-n:]
    
    def collect_governance_dividends(self, agent: str) -> float:
        """Collect governance dividends earned from voting on passed proposals."""
        self._pending_dividends = getattr(self, '_pending_dividends', {})
        amount = self._pending_dividends.pop(agent, 0)
        return round(amount, 2)
    
    def to_dict(self) -> dict:
        """Serialize to dict for persistence."""
        return {
            "params": dict(self.params),
            "proposal_counter": self._proposal_counter,
            "cooldowns": dict(self._cooldowns),
            "dividend_pool": self.dividend_pool,
            "event_log": self.event_log[-50:],  # Keep last 50 events
            # Proposals are not serialized (reset on reload for safety)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WorldParamRegistry":
        """Deserialize from dict."""
        reg = cls()
        if "params" in data:
            for k, v in data["params"].items():
                if k in reg.params:
                    reg.params[k] = v
        if "proposal_counter" in data:
            reg._proposal_counter = data["proposal_counter"]
        if "cooldowns" in data:
            reg._cooldowns = dict(data["cooldowns"])
        if "dividend_pool" in data:
            reg.dividend_pool = data["dividend_pool"]
        if "event_log" in data:
            reg.event_log = data["event_log"]
        return reg
