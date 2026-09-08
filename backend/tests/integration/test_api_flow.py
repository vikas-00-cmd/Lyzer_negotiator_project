import pytest
import uuid
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    app.state.limiter.enabled = False
    yield
    app.state.limiter.enabled = True


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


def test_full_api_flow(client):
    payload = {
        "buyer_max_budget": 50000,
        "buyer_max_delivery_days": 45,
        "buyer_min_sla_percent": 2.0,
        "vendor_min_price": 42000,
        "vendor_min_delivery_days": 30,
        "vendor_max_sla_percent": 5.0,
        "max_rounds": 5
    }

    start_resp = client.post("/api/v1/negotiation/start", json=payload)
    assert start_resp.status_code == 200
    session_id = start_resp.json()["id"]

    status_resp = client.get(f"/api/v1/negotiation/{session_id}/status")
    assert status_resp.status_code == 200

    step_resp = client.post(f"/api/v1/negotiation/{session_id}/step")
    assert step_resp.status_code == 200

    auto_resp = client.post(f"/api/v1/negotiation/{session_id}/auto")
    assert auto_resp.status_code == 200
    assert auto_resp.json()["status"] in ["ACCEPTED", "DEADLOCK"]


def test_api_flow_with_steps(client):
    payload = {
        "buyer_max_budget": 50000,
        "buyer_max_delivery_days": 45,
        "buyer_min_sla_percent": 2.0,
        "vendor_min_price": 42000,
        "vendor_min_delivery_days": 30,
        "vendor_max_sla_percent": 5.0,
        "max_rounds": 3
    }

    start_resp = client.post("/api/v1/negotiation/start", json=payload)
    session_id = start_resp.json()["id"]

    for _ in range(3):
        step_resp = client.post(f"/api/v1/negotiation/{session_id}/step")
        assert step_resp.status_code in [200, 400]

    status_resp = client.get(f"/api/v1/negotiation/{session_id}/status")
    assert status_resp.json()["status"] in ["ACCEPTED", "DEADLOCK", "IN_PROGRESS"]
