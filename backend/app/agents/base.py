"""Abstract base class for all negotiation agents.

Every agent (Buyer, Vendor, or Lyzr-backed) inherits from
:class:`BaseAgent` and must implement :meth:`generate_offer`.
"""

from abc import ABC, abstractmethod
from app.schemas.proposal import ProposalBid, NegotiationState


class BaseAgent(ABC):
    """Base class providing the agent interface for the negotiation loop.

    Attributes:
        agent_type: Identifier string, either ``"BUYER"`` or ``"VENDOR"``.
    """

    def __init__(self, agent_type: str):
        self.agent_type = agent_type

    @abstractmethod
    def generate_offer(self, state: NegotiationState) -> ProposalBid:
        """Generate the next offer or acceptance given the current negotiation state.

        Args:
            state: The full negotiation state including round history.

        Returns:
            A validated proposal bid containing price, delivery, SLA,
            and an action (OFFER, ACCEPT, or END_NEGOTIATION).
        """
        pass
