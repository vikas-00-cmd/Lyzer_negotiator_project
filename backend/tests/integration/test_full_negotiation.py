import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.negotiation import NegotiationSession, NegotiationRound, NegotiationStatus
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


def test_full_negotiation_flow(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    result = run_full_negotiation(db_session, session.id)

    assert result.status in [NegotiationStatus.ACCEPTED, NegotiationStatus.DEADLOCK]
    assert result.current_round >= 1


def test_negotiation_creates_rounds(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    run_full_negotiation(db_session, session.id)

    rounds = db_session.query(NegotiationRound).filter(
        NegotiationRound.session_id == session.id
    ).all()
    assert len(rounds) > 0


def test_contract_created_on_accept(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    result = run_full_negotiation(db_session, session.id)

    if result.status == NegotiationStatus.ACCEPTED:
        contract = db_session.query(Contract).filter(Contract.session_id == session.id).first()
        assert contract is not None
        assert contract.final_price > 0


def test_rounds_logged_with_both_agents(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=5)
    run_full_negotiation(db_session, session.id)

    rounds = db_session.query(NegotiationRound).filter(
        NegotiationRound.session_id == session.id
    ).all()

    agent_types = {r.agent_type for r in rounds}
    assert "BUYER" in agent_types
    assert "VENDOR" in agent_types


def test_pdf_generated_on_accept(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    result = run_full_negotiation(db_session, session.id)

    if result.status == NegotiationStatus.ACCEPTED:
        contract = db_session.query(Contract).filter(Contract.session_id == session.id).first()
        if contract and contract.pdf_file_path:
            assert os.path.exists(contract.pdf_file_path)
            os.remove(contract.pdf_file_path)
