import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.negotiation import NegotiationSession, NegotiationRound
from app.models.contract import Contract
from app.engine.orchestrator import create_session, run_full_negotiation
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_session_persisted(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy)
    retrieved = db_session.query(NegotiationSession).filter(NegotiationSession.id == session.id).first()
    assert retrieved is not None
    assert retrieved.buyer_policy["max_budget"] == 50000


def test_rounds_persisted(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=5)
    run_full_negotiation(db_session, session.id)

    rounds = db_session.query(NegotiationRound).filter(
        NegotiationRound.session_id == session.id
    ).all()
    assert len(rounds) >= 2


def test_round_data_integrity(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=5)
    run_full_negotiation(db_session, session.id)

    rounds = db_session.query(NegotiationRound).filter(
        NegotiationRound.session_id == session.id
    ).all()

    for r in rounds:
        assert r.price > 0
        assert r.delivery_days > 0
        assert r.sla_percent > 0
        assert r.action in ["OFFER", "ACCEPT", "END_NEGOTIATION"]
        assert r.agent_type in ["BUYER", "VENDOR"]
