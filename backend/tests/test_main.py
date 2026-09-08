import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    app.state.limiter.enabled = False
    yield
    app.state.limiter.enabled = True


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_app_initializes(client):
    response = client.get("/")
    assert response.status_code == 200


def test_cors_headers(client):
    response = client.get("/", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_api_v1_prefix(client):
    response = client.get("/api/v1/negotiation/test/status")
    assert response.status_code in [404, 422]
