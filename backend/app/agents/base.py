from abc import ABC, abstractmethod
from app.schemas.proposal import ProposalBid, NegotiationState


class BaseAgent(ABC):
    def __init__(self, agent_type: str):
        self.agent_type = agent_type

    @abstractmethod
    def generate_offer(self, state: NegotiationState) -> ProposalBid:
        pass
