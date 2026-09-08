import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch
from app.database import Base
from app.models.negotiation import NegotiationSession, NegotiationStatus
from app.engine.orchestrator import create_session, run_full_negotiation, run_one_step
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope
from app.schemas.proposal import ProposalBid, ProposalAction, NegotiationState


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def buyer_policy():
    return BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)


@pytest.fixture
def vendor_policy():
    return VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)


def test_create_session(db_session, buyer_policy, vendor_policy):
    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=5)
    assert session.id is not None
    assert session.status == NegotiationStatus.PENDING
    assert session.max_rounds == 5


def test_run_full_negotiation(db_session, buyer_policy, vendor_policy):
    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=5)
    result = run_full_negotiation(db_session, session.id)
    assert result.status in [NegotiationStatus.ACCEPTED, NegotiationStatus.DEADLOCK]


def test_run_one_step(db_session, buyer_policy, vendor_policy):
    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=5)
    state = run_one_step(db_session, session.id)
    assert state.current_round >= 1
    assert len(state.history) > 0


def test_step_increments_round(db_session, buyer_policy, vendor_policy):
    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=5)
    state1 = run_one_step(db_session, session.id)
    state2 = run_one_step(db_session, session.id)
    assert state2.current_round > state1.current_round


def test_invalid_session_id(db_session):
    with pytest.raises(ValueError, match="Session not found"):
        run_full_negotiation(db_session, "invalid-id")


def test_step_invalid_session(db_session):
    with pytest.raises(ValueError, match="Session not found"):
        run_one_step(db_session, "invalid-id")


def test_deadlock_detection(db_session, buyer_policy, vendor_policy):
    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=1)
    result = run_full_negotiation(db_session, session.id)
    assert result.status in [NegotiationStatus.ACCEPTED, NegotiationStatus.DEADLOCK]
