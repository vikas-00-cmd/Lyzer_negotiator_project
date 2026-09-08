import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.negotiation import NegotiationSession, NegotiationStatus
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope
from app.schemas.proposal import ProposalBid, ProposalAction, NegotiationState
from app.agents.base import BaseAgent


class StubbornBuyerAgent(BaseAgent):
    def __init__(self, policy=None):
        super().__init__("BUYER")

    def generate_offer(self, state: NegotiationState) -> ProposalBid:
        return ProposalBid(
            price=40000,
            delivery_days=20,
            sla_percent=5.0,
            action=ProposalAction.OFFER,
            justification="Stubborn buyer",
            round_number=state.current_round,
            agent_type="BUYER"
        )


class StubbornVendorAgent(BaseAgent):
    def __init__(self, policy=None):
        super().__init__("VENDOR")

    def generate_offer(self, state: NegotiationState) -> ProposalBid:
        return ProposalBid(
            price=49000,
            delivery_days=40,
            sla_percent=2.0,
            action=ProposalAction.OFFER,
            justification="Stubborn vendor",
            round_number=state.current_round,
            agent_type="VENDOR"
        )


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_stubborn_agents_trigger_deadlock(db_session):
    from unittest.mock import patch

    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    from app.engine import orchestrator
    session = orchestrator.create_session(db_session, buyer_policy, vendor_policy, max_rounds=3)

    with patch.object(orchestrator, 'BuyerAgent', StubbornBuyerAgent), \
         patch.object(orchestrator, 'VendorAgent', StubbornVendorAgent):
        result = orchestrator.run_full_negotiation(db_session, session.id)

    assert result.status == NegotiationStatus.DEADLOCK
    assert result.current_round <= 3


def test_deadlock_at_exact_max_rounds(db_session):
    from unittest.mock import patch
    from app.engine import orchestrator

    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    for max_rounds in [1, 2, 5, 10]:
        session = orchestrator.create_session(db_session, buyer_policy, vendor_policy, max_rounds=max_rounds)

        with patch.object(orchestrator, 'BuyerAgent', StubbornBuyerAgent), \
             patch.object(orchestrator, 'VendorAgent', StubbornVendorAgent):
            result = orchestrator.run_full_negotiation(db_session, session.id)

        assert result.status == NegotiationStatus.DEADLOCK


def test_no_infinite_loop(db_session):
    from unittest.mock import patch
    from app.engine import orchestrator

    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = orchestrator.create_session(db_session, buyer_policy, vendor_policy, max_rounds=5)

    with patch.object(orchestrator, 'BuyerAgent', StubbornBuyerAgent), \
         patch.object(orchestrator, 'VendorAgent', StubbornVendorAgent):
        result = orchestrator.run_full_negotiation(db_session, session.id)

    assert result.current_round <= 5
    assert result.status == NegotiationStatus.DEADLOCK
