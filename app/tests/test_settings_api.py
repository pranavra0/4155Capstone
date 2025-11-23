import pytest
from fastapi.testclient import TestClient

import main
from api import settings as settings_api


class DummyScheduler:
    def __init__(self, strategy: str = "round_robin"):
        self._strategy = strategy

    def get_strategy(self) -> str:
        return self._strategy

    def set_strategy(self, strategy: str):
        if strategy not in ["first_fit", "round_robin", "resource_aware"]:
            raise ValueError(f"Unknown scheduling strategy: {strategy}")
        self._strategy = strategy


def create_client_with_dummy_scheduler(monkeypatch):
    dummy = DummyScheduler()
    # Patch the scheduler used inside the /settings routes
    monkeypatch.setattr(settings_api, "scheduler", dummy)
    return TestClient(main.app), dummy


def test_get_scheduler_settings(monkeypatch):
    client, dummy = create_client_with_dummy_scheduler(monkeypatch)

    response = client.get("/settings/scheduler")
    assert response.status_code == 200
    data = response.json()

    assert data["strategy"] == dummy.get_strategy()
    assert set(data["available_strategies"]) == {
        "first_fit",
        "round_robin",
        "resource_aware",
    }


def test_update_scheduler_settings_valid(monkeypatch):
    client, dummy = create_client_with_dummy_scheduler(monkeypatch)

    response = client.put("/settings/scheduler", json={"strategy": "first_fit"})
    assert response.status_code == 200
    data = response.json()

    assert data["strategy"] == "first_fit"
    assert "updated to first_fit" in data["message"]
    assert dummy.get_strategy() == "first_fit"


def test_update_scheduler_settings_invalid(monkeypatch):
    client, dummy = create_client_with_dummy_scheduler(monkeypatch)

    response = client.put("/settings/scheduler", json={"strategy": "not-a-strategy"})
    assert response.status_code == 400
    data = response.json()
    assert "Unknown scheduling strategy" in data["detail"]
