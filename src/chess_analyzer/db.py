"""Couche persistance SQLAlchemy 2.x.

Fournit l'engine synchrone, la factory de sessions, la base déclarative et
une dépendance FastAPI pour ouvrir/fermer une session par requête.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from chess_analyzer.config import get_settings


class Base(DeclarativeBase):
    """Base déclarative pour tous les modèles SQLAlchemy du projet."""


_settings = get_settings()

# SQLite a besoin de `check_same_thread=False` pour être utilisé depuis
# plusieurs threads (FastAPI workers / tests). On laisse SQLAlchemy gérer
# la sérialisation des écritures via le pool.
_engine_kwargs: Final[dict] = (
    {"connect_args": {"check_same_thread": False}, "future": True}
    if _settings.database_url.startswith("sqlite")
    else {"future": True}
)

engine = create_engine(_settings.database_url, **_engine_kwargs)

SessionLocal: Final[sessionmaker[Session]] = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI : ouvre une session et la ferme en fin de requête."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
