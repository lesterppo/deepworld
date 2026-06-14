"""
DeepWorld — Voting and legislation system.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Proposal:
    id: str
    title: str
    text: str
    proposer: str
    day: int
    tick: int
    votes_approve: int = 0
    votes_reject: int = 0
    total_voters: int = 10
    needed_approve: int = 7  # 70%
    voters: Dict[str, bool] = field(default_factory=dict)  # agent -> approve
    status: str = "active"  # active, passed, rejected
    urgency: str = "medium"


class VotingSystem:
    """Manages proposals, ballots, and constitutional amendments."""

    def __init__(self, threshold: float = 0.70):
        self.threshold = threshold
        self.active_proposals: Dict[str, Proposal] = {}
        self.passed_laws: List[Dict[str, Any]] = []
        self.rejected_proposals: List[Dict[str, Any]] = []
        self.proposal_counter = 0

    def create_proposal(
        self, title: str, text: str, proposer: str, day: int, tick: int,
        total_voters: int = 10, urgency: str = "medium",
    ) -> str:
        """Create a new proposal, return its ID."""
        self.proposal_counter += 1
        prop_id = f"P{self.proposal_counter:03d}"
        needed = max(1, int(total_voters * self.threshold))
        self.active_proposals[prop_id] = Proposal(
            id=prop_id,
            title=title,
            text=text,
            proposer=proposer,
            day=day,
            tick=tick,
            total_voters=total_voters,
            needed_approve=needed,
            urgency=urgency,
        )
        return prop_id

    def cast_ballot(self, proposal_id: str, agent_name: str, approve: bool) -> Dict[str, Any]:
        """Cast a vote. Returns status update."""
        if proposal_id not in self.active_proposals:
            return {"error": f"Proposal {proposal_id} not found"}

        prop = self.active_proposals[proposal_id]
        if agent_name in prop.voters:
            return {"error": f"{agent_name} already voted on {proposal_id}"}

        prop.voters[agent_name] = approve
        if approve:
            prop.votes_approve += 1
        else:
            prop.votes_reject += 1

        # Check if passed or failed
        alive_voters = prop.total_voters  # simplified — in real sim, adjust for deaths
        if prop.votes_approve >= prop.needed_approve:
            prop.status = "passed"
            self.passed_laws.append({
                "id": prop.id,
                "title": prop.title,
                "text": prop.text,
                "proposer": prop.proposer,
                "approve": prop.votes_approve,
                "reject": prop.votes_reject,
            })
            del self.active_proposals[proposal_id]
            return {"status": "passed", "proposal": prop}
        elif prop.votes_reject > (alive_voters - prop.needed_approve):
            prop.status = "rejected"
            self.rejected_proposals.append({
                "id": prop.id,
                "title": prop.title,
                "proposer": prop.proposer,
                "approve": prop.votes_approve,
                "reject": prop.votes_reject,
            })
            del self.active_proposals[proposal_id]
            return {"status": "rejected", "proposal": prop}

        return {"status": "pending", "proposal": prop}

    def get_active_for_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get active proposals an agent hasn't voted on yet."""
        active = []
        for prop_id, prop in self.active_proposals.items():
            if agent_name not in prop.voters:
                active.append({
                    "id": prop.id,
                    "title": prop.title,
                    "text": prop.text,
                    "proposer": prop.proposer,
                    "approve": prop.votes_approve,
                    "total_voters": prop.total_voters,
                    "needed_approve": prop.needed_approve,
                    "urgency": prop.urgency,
                })
        return active

    def expire_old_proposals(self, current_day: int, current_tick: int, max_age_ticks: int = 12):
        """Expire proposals that are too old."""
        expired = []
        for prop_id, prop in list(self.active_proposals.items()):
            age = (current_day - prop.day) * 12 + (current_tick - prop.tick)
            if age > max_age_ticks:
                prop.status = "expired"
                expired.append(prop_id)
                del self.active_proposals[prop_id]
        return expired
