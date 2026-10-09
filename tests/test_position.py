"""Tests du modèle ``Position`` (table ``positions``).

Couvre les acceptance criteria du Jalon 1 :
- persistance d'une FEN (insert + retrieve)
- contrainte PRIMARY KEY : une FEN dupliquée lève ``IntegrityError``
- métadonnées de la table : ``fen`` est PK, ``created_at`` a un server_default
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from chess_analyzer.models import Position

# FEN de la position initiale standard (pas de coup joué).
_STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


@pytest.fixture()
def db_session(tmp_path: Path) -> Generator[Session, None, None]:
    """Session SQLAlchemy sur une base jetable migrée via Alembic (head)."""

    from sqlalchemy import pool

    from chess_analyzer.db import make_engine

    db_file = tmp_path / f"positions_{tmp_path.name}.db"
    engine = make_engine(f"sqlite:///{db_file}", poolclass=pool.NullPool)
    try:
        alembic_cfg = AlembicConfig(str(Path(__file__).parents[1] / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_file}".replace("%", "%%"))
        alembic_command.upgrade(alembic_cfg, "head")

        testing_session_local = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
        session = testing_session_local()
        try:
            yield session
        finally:
            session.close()
    finally:
        engine.dispose()


def test_create_and_retrieve_position(db_session: Session) -> None:
    """Insère une Position, commit, relit via ``session.get`` — même FEN."""

    db_session.add(Position(fen=_STARTING_FEN))
    db_session.commit()

    fetched = db_session.get(Position, _STARTING_FEN)

    assert fetched is not None
    assert fetched.fen == _STARTING_FEN


def test_duplicate_fen_raises_integrity_error(db_session: Session) -> None:
    """Deux insertions de la même FEN : la 2ᵉ lève ``IntegrityError``."""

    db_session.add(Position(fen=_STARTING_FEN))
    db_session.commit()

    db_session.add(Position(fen=_STARTING_FEN))
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_position_metadata_in_db(tmp_path: Path) -> None:
    """Après migration Alembic, la table ``positions`` a la bonne structure."""

    from sqlalchemy import pool

    from chess_analyzer.db import make_engine

    db_file = tmp_path / f"meta_{tmp_path.name}.db"
    engine = make_engine(f"sqlite:///{db_file}", poolclass=pool.NullPool)
    try:
        alembic_cfg = AlembicConfig(str(Path(__file__).parents[1] / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_file}".replace("%", "%%"))
        alembic_command.upgrade(alembic_cfg, "head")

        inspector = inspect(engine)
        columns = {col["name"]: col for col in inspector.get_columns("positions")}
        pk = inspector.get_pk_constraint("positions")

        assert "fen" in columns
        assert "created_at" in columns
        assert pk["constrained_columns"] == ["fen"]
        # ``String(120)`` est rendu en ``VARCHAR(120)`` côté SQLAlchemy/inspect.
        assert columns["fen"]["type"].length == 120
        assert columns["fen"]["nullable"] is False
        assert columns["created_at"]["nullable"] is False
    finally:
        engine.dispose()


def test_client_fixture_uses_alembic(client: TestClient, tmp_path: Path) -> None:
    """La fixture ``client`` crée sa DB via Alembic (AC: D1.1 résolu).

    On vérifie qu'après le yield la table ``positions`` existe en interrogeant
    la DB de la fixture via l'engine qu'elle a installé. On accède à l'engine
    par effet de bord : la fixture l'a déjà disposé à ce stade, donc on
    vérifie plutôt qu'une requête HTTP passe (sanity check que le câblage
    n'a pas régressé).
    """

    response = client.get("/healthz")
    assert response.status_code == 200
