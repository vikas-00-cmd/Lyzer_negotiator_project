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


def test_contract_matches_agreed_terms(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    result = run_full_negotiation(db_session, session.id)

    if result.status == NegotiationStatus.ACCEPTED:
        contract = db_session.query(Contract).filter(Contract.session_id == session.id).first()
        assert contract is not None
        assert contract.final_price >= vendor_policy.min_price
        assert contract.final_price <= buyer_policy.max_budget
        assert contract.final_delivery_days >= vendor_policy.min_delivery_days
        assert contract.final_delivery_days <= buyer_policy.max_delivery_days
        assert contract.final_sla_percent >= buyer_policy.min_sla_percent
        assert contract.final_sla_percent <= vendor_policy.max_sla_percent


def test_pdf_file_is_valid(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    result = run_full_negotiation(db_session, session.id)

    if result.status == NegotiationStatus.ACCEPTED:
        contract = db_session.query(Contract).filter(Contract.session_id == session.id).first()
        if contract and contract.pdf_file_path and os.path.exists(contract.pdf_file_path):
            with open(contract.pdf_file_path, "rb") as f:
                content = f.read()
            assert content[:5] == b'%PDF-'
            assert len(content) > 100
            os.remove(contract.pdf_file_path)


def test_contract_final_price_in_range(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    result = run_full_negotiation(db_session, session.id)

    if result.status == NegotiationStatus.ACCEPTED:
        contract = db_session.query(Contract).filter(Contract.session_id == session.id).first()
        assert 42000 <= contract.final_price <= 50000


def test_contract_delivery_in_range(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    result = run_full_negotiation(db_session, session.id)

    if result.status == NegotiationStatus.ACCEPTED:
        contract = db_session.query(Contract).filter(Contract.session_id == session.id).first()
        assert 30 <= contract.final_delivery_days <= 45


def test_contract_sla_in_range(db_session):
    buyer_policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    vendor_policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)

    session = create_session(db_session, buyer_policy, vendor_policy, max_rounds=10)
    result = run_full_negotiation(db_session, session.id)

    if result.status == NegotiationStatus.ACCEPTED:
        contract = db_session.query(Contract).filter(Contract.session_id == session.id).first()
        assert 2.0 <= contract.final_sla_percent <= 5.0
