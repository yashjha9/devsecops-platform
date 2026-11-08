import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["message"] == "Welcome to SecureRelease"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_version_endpoint(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json["version"] == "1.0.0"
