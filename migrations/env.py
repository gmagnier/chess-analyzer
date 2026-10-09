"""Configuration Alembic (mode synchrone) pour chess-analyzer.

Câble Alembic au moteur SQLAlchemy de l'application : l'URL de connexion
provient de ``chess_analyzer.config.get_settings().database_url`` (qui
supporte l'override par variable d'environnement ou fichier .env), et la
cible d'autogénération est ``chess_analyzer.db.Base.metadata``.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from chess_analyzer.config import get_settings
from chess_analyzer.db import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# On surcharge sqlalchemy.url avec la valeur de l'application, pour qu'une
# seule source de vérité configure la base (Settings + .env).
database_url = get_settings().database_url
# ConfigParser interprète les %, y compris ceux des identifiants encodés.
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Cible d'autogénération : metadata de la base déclarative du projet.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
