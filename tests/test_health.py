"""Tests de la sonde de vie ``GET /healthz``."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthz_returns_ok_json(client: TestClient) -> None:
    """``GET /healthz`` doit renvoyer 200 et un JSON ``{"status": "ok"}``."""

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"status": "ok"}