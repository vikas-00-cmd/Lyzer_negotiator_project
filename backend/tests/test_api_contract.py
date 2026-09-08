import pytest
import uuid
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.negotiation import NegotiationSession
from app.models.contract import Contract


@pytest.fixture
def client():
    db_name = f"test_{uuid.uuid4().hex}.db"
    db_url = f"sqlite:///{db_name}"
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()
    if os.path.exists(db_name):
        os.remove(db_name)


@pytest.fixture
def db_with_contract():
    db_name = f"test_{uuid.uuid4().hex}.db"
    db_url = f"sqlite:///{db_name}"
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    db = TestSession()

    neg_session = NegotiationSession(
        buyer_policy={"max_budget": 50000},
        vendor_policy={"min_price": 42000}
    )
    db.add(neg_session)
    db.commit()

    contract = Contract(
        session_id=neg_session.id,
        final_price=45500,
        final_delivery_days=35,
        final_sla_percent=3.5
    )
    db.add(contract)
    db.commit()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield neg_session.id, db_name
    app.dependency_overrides.clear()
    db.close()
    engine.dispose()
    if os.path.exists(db_name):
        os.remove(db_name)


def test_get_contract_details(client, db_with_contract):
    session_id, _ = db_with_contract
    response = client.get(f"/api/v1/contract/{session_id}/details")
    assert response.status_code == 200
    assert response.json()["final_price"] == 45500


def test_get_contract_not_found(client):
    response = client.get("/api/v1/contract/nonexistent/details")
    assert response.status_code == 404


def test_get_contract_pdf_not_found(client, db_with_contract):
    session_id, _ = db_with_contract
    response = client.get(f"/api/v1/contract/{session_id}/pdf")
    assert response.status_code == 404
