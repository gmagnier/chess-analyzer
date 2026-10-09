"""Fixtures partagées par la suite de tests.

Fournit un ``TestClient`` FastAPI avec une base SQLite jetable par test
(``<tmp_path>/test_<rand>.db``) injectée via la dépendance ``get_db``.

La DB de test est créée via ``alembic.command.upgrade(alembic_cfg, "head")``
et non via ``Base.metadata.create_all`` : on veut que la fixture suive
fidèlement le schéma de production, pas une version parallèle construite
uniquement pour les tests (cf. deferred D1.1).

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
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from chess_analyzer.db import get_db
from chess_analyzer.main import app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    """Client HTTP de test avec une base SQLite jetable migrée via Alembic."""

    db_file = tmp_path / f"test_{uuid.uuid4().hex}.db"
    test_engine = _create_alembic_managed_engine(db_file)

    testing_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
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


def _create_alembic_managed_engine(db_file: Path) -> Engine:
    """Crée un engine SQLite jetable et applique toutes les migrations Alembic.

    On réutilise ``make_engine`` (pas de duplication de kwargs) et on force
    ``NullPool`` pour que chaque migration (et chaque test) ouvre/ferme
    sa propre connexion — évite les verrous SQLite résiduels entre tests.
    """

    from sqlalchemy import pool

    from chess_analyzer.db import make_engine

    db_url = f"sqlite:///{db_file}"

    # ``env.py`` construit son propre engine via ``make_engine(url)`` et
    # applique les migrations. On construit ensuite un engine séparé pour
    # la session de test (mêmes kwargs, juste un pool distinct). Les deux
    # engines partagent la même DB SQLite sur disque.
    alembic_cfg = AlembicConfig(str(Path(__file__).parents[1] / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", db_url.replace("%", "%%"))
    alembic_command.upgrade(alembic_cfg, "head")

    test_engine = make_engine(db_url, poolclass=pool.NullPool)
    return test_engine
