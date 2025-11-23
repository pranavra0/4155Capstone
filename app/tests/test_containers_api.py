from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import main
from api import containers as containers_api


class DummyContainer:
    """Mimics the minimal interface of a Docker container used in _serialize."""

    def __init__(self, cid: str, name: str, image: str, status: str):
        self.id = cid
        self.name = name
        # Image object with .tags list, like docker SDK
        self.image = SimpleNamespace(tags=[image])
        self.status = status


class DummyContainerManager:
    def __init__(self):
        self._containers = [
            DummyContainer("abc123", "test-container", "nginx:latest", "running")
        ]

    async def list_containers_async(self, all: bool = False):
        return list(self._containers)

    async def get_container_async(self, container_id: str):
        # Always return the first one for simplicity
        return self._containers[0]

    async def start_container_async(self, image: str, name: str | None = None):
        # Pretend we created a new container
        return {
            "id": "new123",
            "name": name,
            "image": image,
            "status": "running",
        }

    async def stop_container_async(self, container_id: str, remove: bool = True):
        return {"id": container_id, "status": "removed" if remove else "stopped"}


def create_client_with_dummy_manager(monkeypatch):
    dummy_manager = DummyContainerManager()
    # Patch the container_manager used by the routes
    monkeypatch.setattr(containers_api, "container_manager", dummy_manager)
    return TestClient(main.app), dummy_manager


def test_list_containers_uses_dummy_manager(monkeypatch):
    client, dummy = create_client_with_dummy_manager(monkeypatch)

    response = client.get("/containers")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert data, "Expected at least one container in response"
    first = data[0]
    assert first["id"] == "abc123"
    assert first["name"] == "test-container"
    assert first["image"] == "nginx:latest"
    assert first["status"] == "running"


def test_get_container_uses_dummy_manager(monkeypatch):
    client, dummy = create_client_with_dummy_manager(monkeypatch)

    response = client.get("/containers/abc123")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "abc123"
    assert data["name"] == "test-container"


def test_create_container_uses_dummy_manager(monkeypatch):
    client, dummy = create_client_with_dummy_manager(monkeypatch)

    response = client.post(
        "/containers",
        params={"image": "redis:latest", "name": "redis-test"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "new123"
    assert data["image"] == "redis:latest"
    assert data["name"] == "redis-test"


def test_delete_container_uses_dummy_manager(monkeypatch):
    client, dummy = create_client_with_dummy_manager(monkeypatch)

    response = client.delete("/containers/abc123")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "abc123"
    assert data["status"] == "removed"
