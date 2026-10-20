
import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Give every test its own temporary database.
    monkeypatch.setattr(
        main, "DATABASE_PATH", tmp_path / "test_flags.db"
    )

    with TestClient(main.app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_flag(client):
    response = client.post(
        "/flags",
        json={"name": "new_dashboard", "enabled": False},
    )

    assert response.status_code == 201
    assert response.json() == {
        "name": "new_dashboard",
        "enabled": False,
    }


def test_duplicate_flag_returns_conflict(client):
    payload = {"name": "checkout", "enabled": True}

    assert client.post("/flags", json=payload).status_code == 201

    response = client.post("/flags", json=payload)

    assert response.status_code == 409


def test_invalid_flag_name_is_rejected(client):
    response = client.post(
        "/flags",
        json={"name": "bad flag name", "enabled": True},
    )

    assert response.status_code == 422


def test_update_flag(client):
    client.post(
        "/flags",
        json={"name": "dark_mode", "enabled": False},
    )

    response = client.patch(
        "/flags/dark_mode",
        json={"enabled": True},
    )

    assert response.status_code == 200
    assert response.json()["enabled"] is True


def test_unknown_flag_evaluates_to_false(client):
    response = client.get("/flags/not_created/evaluate")

    assert response.status_code == 200
    assert response.json() == {
        "name": "not_created",
        "enabled": False,
    }


def test_missing_flag_update_returns_404(client):
    response = client.patch(
        "/flags/missing",
        json={"enabled": True},
    )

    assert response.status_code == 404


def test_flag_persists_after_app_restart(tmp_path, monkeypatch):
    database = tmp_path / "persistent_flags.db"
    monkeypatch.setattr(main, "DATABASE_PATH", database)

    # First application session: create a flag.
    with TestClient(main.app) as first_client:
        response = first_client.post(
            "/flags",
            json={"name": "saved_flag", "enabled": True},
        )
        assert response.status_code == 201

    # Second application session: verify the flag still exists.
    with TestClient(main.app) as second_client:
        response = second_client.get("/flags/saved_flag/evaluate")

        assert response.status_code == 200
        assert response.json()["enabled"] is True
