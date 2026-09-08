import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.negotiation import NegotiationSession, NegotiationStatus
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


def test_convergence_within_max_rounds(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    for max_rounds in [5, 10, 15, 20]:
        session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=max_rounds)
        result = run_full_negotiation(db_session, session.id)
        assert result.current_round <= max_rounds


def test_convergence_with_tight_policies(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    result = run_full_negotiation(db_session, session.id)
    assert result.status in [NegotiationStatus.ACCEPTED, NegotiationStatus.DEADLOCK]


def test_convergence_with_relaxed_policies(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=15)
    result = run_full_negotiation(db_session, session.id)
    assert result.status in [NegotiationStatus.ACCEPTED, NegotiationStatus.DEADLOCK]


def test_multiple_negotiations_converge(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    results = []
    for _ in range(10):
        session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
        result = run_full_negotiation(db_session, session.id)
        results.append(result.status)

    accepted = sum(1 for s in results if s == NegotiationStatus.ACCEPTED)
    assert accepted > 0
