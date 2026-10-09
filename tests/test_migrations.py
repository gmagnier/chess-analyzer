"""Vérifie la transmission des URL contenant des % à Alembic."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


@pytest.mark.parametrize("offline", [False, True])
def test_percent_in_migration_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, offline: bool
) -> None:
    database_url = f"sqlite:///{tmp_path / 'encoded%25.db'}"
    monkeypatch.setenv("CHESS_ANALYZER_DATABASE_URL", database_url)
    config = _migration_config()

    command.upgrade(config, "head", sql=offline)

    assert config.get_main_option("sqlalchemy.url") == database_url
    if not offline:
        engine = create_engine(database_url)
        try:
            assert "alembic_version" in inspect(engine).get_table_names()
        finally:
            engine.dispose()


def test_encoded_credentials_in_offline_migration(monkeypatch: pytest.MonkeyPatch) -> None:
    database_url = "postgresql://test:p%40ss%25word@localhost/test"
    monkeypatch.setenv("CHESS_ANALYZER_DATABASE_URL", database_url)
    config = _migration_config()

    command.upgrade(config, "head", sql=True)

    assert config.get_main_option("sqlalchemy.url") == database_url


def _migration_config() -> Config:
    config = Config(output_buffer=StringIO())
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "migrations"))
    return config
