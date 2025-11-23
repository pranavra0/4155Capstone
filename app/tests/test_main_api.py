import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client():
    # Each test gets a fresh TestClient so lifespan hooks run cleanly
    return TestClient(main.app)


def test_root_returns_metadata(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Container Orchestrator API"
    # Basic sanity checks for links the frontend relies on
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


def test_health_returns_ok_and_node_count(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    # Node count can legitimately be 0 if no nodes registered yet,
    # so we just verify it's an integer.
    assert isinstance(data["nodes"], int)
