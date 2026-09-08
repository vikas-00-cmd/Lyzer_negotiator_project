import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.negotiation import NegotiationSession, NegotiationRound, NegotiationStatus


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_session(db_session):
    session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(session)
    db_session.commit()
    assert session.id is not None
    assert session.status == NegotiationStatus.PENDING


def test_session_default_rounds(db_session):
    session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(session)
    db_session.commit()
    assert session.max_rounds == 10
    assert session.current_round == 0


def test_create_round(db_session):
    session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(session)
    db_session.commit()

    round_record = NegotiationRound(
        session_id=session.id,
        round_number=1,
        agent_type="BUYER",
        price=45000,
        delivery_days=30,
        sla_percent=3.5,
        action="OFFER",
        justification="Test"
    )
    db_session.add(round_record)
    db_session.commit()
    assert round_record.id is not None
    assert round_record.session_id == session.id


def test_session_rounds_relationship(db_session):
    session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(session)
    db_session.commit()

    round1 = NegotiationRound(
        session_id=session.id, round_number=1, agent_type="BUYER",
        price=45000, delivery_days=30, sla_percent=3.5, action="OFFER"
    )
    round2 = NegotiationRound(
        session_id=session.id, round_number=1, agent_type="VENDOR",
        price=47000, delivery_days=35, sla_percent=3.0, action="OFFER"
    )
    db_session.add_all([round1, round2])
    db_session.commit()

    assert len(session.rounds) == 2


def test_session_status_update(db_session):
    session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db_session.add(session)
    db_session.commit()

    session.status = NegotiationStatus.IN_PROGRESS
    db_session.commit()
    assert session.status == NegotiationStatus.IN_PROGRESS
