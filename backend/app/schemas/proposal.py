from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class ProposalAction(str, Enum):
    OFFER = "OFFER"
    ACCEPT = "ACCEPT"
    END_NEGOTIATION = "END_NEGOTIATION"


class ProposalBid(BaseModel):
    price: float = Field(..., gt=0, description="Proposed price")
    delivery_days: int = Field(..., gt=0, description="Proposed delivery in days")
    sla_percent: float = Field(..., gt=0, le=100, description="Proposed SLA penalty percent")
    action: ProposalAction = Field(default=ProposalAction.OFFER, description="Action type")
    justification: str = Field(default="", description="Agent rationale")
    round_number: int = Field(default=1, ge=1, description="Current round number")
    agent_type: str = Field(..., description="BUYER or VENDOR")


class NegotiationState(BaseModel):
    session_id: str
    current_round: int = 1
    max_rounds: int = 10
    history: list[ProposalBid] = Field(default_factory=list)
    is_complete: bool = False
    consensus: Optional[ProposalBid] = None
