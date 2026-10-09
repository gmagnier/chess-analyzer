"""Fixtures partagées par la suite de tests.

Fournit un ``TestClient`` FastAPI avec une base SQLite jetable par test
(``<tmp_path>/test_<rand>.db``) injectée via la dépendance ``get_db``.

Les routes actuelles n'utilisent pas encore la persistance, mais le câblage
est posé pour que les futurs tests métier (Jalon 1+) n'aient plus qu'à
utiliser la fixture ``client``.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from chess_analyzer.db import Base, get_db
from chess_analyzer.main import app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    """Client HTTP de test avec une base SQLite jetable dans ``tmp_path``."""

    db_file = tmp_path / f"test_{uuid.uuid4().hex}.db"
    test_engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(test_engine)

    testing_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    def _override_get_db() -> Generator[Session, None, None]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        test_engine.dispose()
        # best-effort cleanup ; tmp_path est nettoyé par pytest de toute façon
        if db_file.exists():
            os.unlink(db_file)
