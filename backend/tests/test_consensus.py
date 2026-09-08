import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.negotiation import NegotiationSession
from app.models.contract import Contract
from app.schemas.proposal import NegotiationState, ProposalBid, ProposalAction
from app.engine.consensus import generate_contract


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_generate_contract(db_session):
    neg_session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(neg_session)
    db_session.commit()

    state = NegotiationState(session_id=neg_session.id, current_round=3)
    state.history = [
        ProposalBid(price=40000, delivery_days=20, sla_percent=5.0, agent_type="BUYER", action=ProposalAction.OFFER, round_number=1),
        ProposalBid(price=49000, delivery_days=40, sla_percent=2.0, agent_type="VENDOR", action=ProposalAction.OFFER, round_number=1),
        ProposalBid(price=44000, delivery_days=30, sla_percent=4.0, agent_type="BUYER", action=ProposalAction.OFFER, round_number=2),
        ProposalBid(price=45500, delivery_days=35, sla_percent=3.5, agent_type="VENDOR", action=ProposalAction.ACCEPT, round_number=2),
    ]
    state.consensus = state.history[-1]

    contract = generate_contract(db_session, neg_session, state)
    assert contract is not None
    assert contract.final_price == 45500
    assert contract.final_delivery_days == 35
    assert contract.final_sla_percent == 3.5
    assert contract.pdf_file_path != ""


def test_pdf_file_created(db_session):
    neg_session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(neg_session)
    db_session.commit()

    state = NegotiationState(session_id=neg_session.id, current_round=2)
    state.history = [
        ProposalBid(price=45000, delivery_days=30, sla_percent=3.5, agent_type="BUYER", action=ProposalAction.OFFER, round_number=1),
        ProposalBid(price=45500, delivery_days=35, sla_percent=3.0, agent_type="VENDOR", action=ProposalAction.ACCEPT, round_number=1),
    ]
    state.consensus = state.history[-1]

    contract = generate_contract(db_session, neg_session, state)
    assert os.path.exists(contract.pdf_file_path)
    os.remove(contract.pdf_file_path)


def test_contract_stored_in_db(db_session):
    neg_session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(neg_session)
    db_session.commit()

    state = NegotiationState(session_id=neg_session.id, current_round=2)
    state.history = [
        ProposalBid(price=45000, delivery_days=30, sla_percent=3.5, agent_type="BUYER", action=ProposalAction.OFFER, round_number=1),
        ProposalBid(price=45500, delivery_days=35, sla_percent=3.0, agent_type="VENDOR", action=ProposalAction.ACCEPT, round_number=1),
    ]
    state.consensus = state.history[-1]

    generate_contract(db_session, neg_session, state)
    stored = db_session.query(Contract).filter(Contract.session_id == neg_session.id).first()
    assert stored is not None
    assert stored.final_price == 45500
