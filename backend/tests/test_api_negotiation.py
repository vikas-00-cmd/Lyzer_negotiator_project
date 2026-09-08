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


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_start_negotiation(client):
    payload = {
        "buyer_max_budget": 50000,
        "buyer_max_delivery_days": 45,
        "buyer_min_sla_percent": 2.0,
        "vendor_min_price": 42000,
        "vendor_min_delivery_days": 30,
        "vendor_max_sla_percent": 5.0,
        "max_rounds": 5
    }
    response = client.post("/api/v1/negotiation/start", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "PENDING"


def test_get_status(client):
    payload = {
        "buyer_max_budget": 50000,
        "buyer_max_delivery_days": 45,
        "buyer_min_sla_percent": 2.0,
        "vendor_min_price": 42000,
        "vendor_min_delivery_days": 30,
        "vendor_max_sla_percent": 5.0
    }
    start_resp = client.post("/api/v1/negotiation/start", json=payload)
    session_id = start_resp.json()["id"]

    response = client.get(f"/api/v1/negotiation/{session_id}/status")
    assert response.status_code == 200
    assert response.json()["id"] == session_id


def test_get_status_not_found(client):
    response = client.get("/api/v1/negotiation/nonexistent/status")
    assert response.status_code == 404


def test_auto_negotiate(client):
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
    session_id = start_resp.json()["id"]

    response = client.post(f"/api/v1/negotiation/{session_id}/auto")
    assert response.status_code == 200
    assert response.json()["status"] in ["ACCEPTED", "DEADLOCK"]


def test_step_negotiation(client):
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
    session_id = start_resp.json()["id"]

    response = client.post(f"/api/v1/negotiation/{session_id}/step")
    assert response.status_code == 200
    assert "history" in response.json()
