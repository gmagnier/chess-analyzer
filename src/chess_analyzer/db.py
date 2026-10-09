"""Couche persistance SQLAlchemy 2.x.

Fournit l'engine synchrone, la factory de sessions, la base déclarative et
une dépendance FastAPI pour ouvrir/fermer une session par requête.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any, Final
from urllib.parse import unquote, urlsplit

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from chess_analyzer.config import get_settings


class Base(DeclarativeBase):
    """Base déclarative pour tous les modèles SQLAlchemy du projet."""


def make_engine(url: str, **kwargs: Any) -> Engine:
    """Construit un ``Engine`` SQLAlchemy à partir d'une URL.

    Encapsule le conditionnel SQLite (``check_same_thread=False``) et force
    le style 2.x (``future=True``). C'est le point central pour les kwargs
    partagés entre l'application et les migrations Alembic — éviter la
    duplication entre ``db.py`` et ``migrations/env.py`` (cf. deferred D1.2).
    """

    parsed_url = make_url(url)
    # ``future=True`` est le défaut SQLAlchemy 2.x et ne peut pas être
    # surchargé (refus explicite pour éviter une régression silencieuse
    # vers le style 1.x si un appelant passe future=False).
    kwargs.pop("future", None)
    engine_kwargs: dict[str, Any] = {"future": True, **kwargs}
    if parsed_url.get_backend_name() == "sqlite" and "connect_args" not in engine_kwargs:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(parsed_url, **engine_kwargs)


_settings = get_settings()
_database_url = make_url(_settings.database_url)

engine = make_engine(_settings.database_url)


# Si la base est un fichier SQLite, on crée le répertoire parent s'il
# n'existe pas — SQLAlchemy ne le fait pas automatiquement et un volume
# vide (Docker, CI fresh) ne contiendrait pas `data/`. No-op pour les
# URL non-fichier (sqlite:///:memory:, postgresql://, etc.).
if _database_url.get_backend_name() == "sqlite":
    db_path_str = _database_url.database
    # Réutiliser la conversion SQLAlchemy de l'option booléenne `uri`.
    _, db_connect_options = engine.dialect.create_connect_args(_database_url)
    if db_path_str and db_path_str.startswith("file:") and db_connect_options.get("uri"):
        db_path_str = unquote(urlsplit(db_path_str).path)
        if _database_url.query.get("mode") == "memory":
            db_path_str = None
    if db_path_str and db_path_str != ":memory:":
        Path(db_path_str).parent.mkdir(parents=True, exist_ok=True)

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
