import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.negotiation import NegotiationSession, NegotiationStatus
from app.models.contract import Contract


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_contract(db_session):
    neg_session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(neg_session)
    db_session.commit()

    contract = Contract(
        session_id=neg_session.id,
        final_price=45500,
        final_delivery_days=35,
        final_sla_percent=3.5,
        pdf_file_path="./contracts/test.pdf"
    )
    db_session.add(contract)
    db_session.commit()
    assert contract.id is not None
    assert contract.session_id == neg_session.id


def test_contract_session_relationship(db_session):
    neg_session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(neg_session)
    db_session.commit()

    contract = Contract(
        session_id=neg_session.id,
        final_price=45500,
        final_delivery_days=35,
        final_sla_percent=3.5
    )
    db_session.add(contract)
    db_session.commit()

    assert neg_session.contract is not None
    assert neg_session.contract.final_price == 45500


def test_contract_pdf_path_default():
    contract = Contract(
        session_id="test-session",
        final_price=45500,
        final_delivery_days=35,
        final_sla_percent=3.5
    )
    assert contract.pdf_file_path is None or contract.pdf_file_path == ""


def test_contract_unique_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    neg_session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    session.add(neg_session)
    session.commit()

    contract1 = Contract(
        session_id=neg_session.id,
        final_price=45500,
        final_delivery_days=35,
        final_sla_percent=3.5
    )
    session.add(contract1)
    session.commit()

    contract2 = Contract(
        session_id=neg_session.id,
        final_price=46000,
        final_delivery_days=40,
        final_sla_percent=4.0
    )
    session.add(contract2)
    try:
        session.commit()
        session.rollback()
        pytest.fail("Should have raised integrity error for duplicate session_id")
    except Exception:
        session.rollback()

    session.close()
