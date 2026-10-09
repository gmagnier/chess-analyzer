"""Tests de la page d'accueil ``GET /``."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_root_returns_html_with_title(client: TestClient) -> None:
    """``GET /`` doit renvoyer 200 et une page HTML contenant le titre."""

    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>chess-analyzer</title>" in response.text