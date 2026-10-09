"""Vérifie les chemins SQLite dans un processus isolé (configuration à l'import)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("database_url", "database_path"),
    [
        ("sqlite:///./data/new.db", "data/new.db"),
        ("sqlite+pysqlite:///./data/new.db?timeout=10", "data/new.db"),
        ("sqlite:///file:./data/new.db?mode=rwc&uri=true", "data/new.db"),
        ("sqlite:///file:./data/new.db?mode=rwc&uri=1", "data/new.db"),
        ("sqlite:///file:./data%20dir/new.db?mode=rwc&uri=true", "data dir/new.db"),
        ("sqlite:///file:./data/new.db?uri=false", "file:./data/new.db"),
        ("sqlite:///./data/:memory:.db", "data/:memory:.db"),
        ("sqlite://", None),
        ("sqlite:///:memory:", None),
        ("sqlite:///file::memory:?cache=shared&uri=true", None),
        ("sqlite:///file:./data/shared?mode=memory&cache=shared&uri=true", None),
    ],
)
def test_sqlite_database_path(tmp_path: Path, database_url: str, database_path: str | None) -> None:
    _connect_in_subprocess(tmp_path, database_url)

    if database_path is None:
        assert list(tmp_path.iterdir()) == []
    else:
        expected_path = tmp_path / database_path
        assert expected_path.is_file()
        assert {path for path in tmp_path.rglob("*") if path.is_file()} == {expected_path}
        assert {path for path in tmp_path.rglob("*") if path.is_dir()} == set(
            expected_path.parents
        ) - set(tmp_path.parents) - {tmp_path}


@pytest.mark.parametrize("uri", [False, True])
def test_absolute_sqlite_database_path(tmp_path: Path, uri: bool) -> None:
    database_path = tmp_path / "data" / "new.db"
    database_url = (
        f"sqlite:///file:{database_path}?mode=rwc&uri=true" if uri else f"sqlite:///{database_path}"
    )
    _connect_in_subprocess(tmp_path, database_url)
    assert database_path.is_file()
    assert not (tmp_path / "file:").exists()


def _connect_in_subprocess(directory: Path, database_url: str) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from chess_analyzer.db import engine\n"
            "with engine.begin() as connection:\n"
            "    connection.exec_driver_sql('CREATE TABLE smoke (id INTEGER PRIMARY KEY)')\n"
            "engine.dispose()\n",
        ],
        cwd=directory,
        env={**os.environ, "CHESS_ANALYZER_DATABASE_URL": database_url},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
