"""Configuration Alembic (mode synchrone) pour chess-analyzer.

Câble Alembic au moteur SQLAlchemy de l'application : l'URL de connexion
provient de ``chess_analyzer.config.get_settings().database_url`` (qui
supporte l'override par variable d'environnement ou fichier .env), et la
cible d'autogénération est ``chess_analyzer.db.Base.metadata``.

L'engine utilisé pour les migrations est construit via ``make_engine``
(``chess_analyzer.db``) pour partager les kwargs (conditionnel SQLite,
``future=True``) avec le code applicatif — évite la duplication entre
``db.py`` et ``migrations/env.py`` (cf. deferred D1.2).
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

# Importer ``models`` pour enregistrer les mappings sur ``Base.metadata``
# avant l'autogénération. Sans cet import, ``alembic revision
# --autogenerate`` ne voit aucune table applicative et produit une révision
# vide. L'import dans ``main.py`` couvre le runtime applicatif ; celui-ci
# couvre la session Alembic (ligne de commande).
import chess_analyzer.models  # noqa: F401, E402
from chess_analyzer.config import get_settings
from chess_analyzer.db import Base, make_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# On surcharge sqlalchemy.url avec la valeur de l'application, pour qu'une
# seule source de vérité configure la base (Settings + .env). Mais si une
# URL est déjà dans la config (cas des tests programmatiques qui créent
# un ``AlembicConfig`` et setent ``sqlalchemy.url``), on la respecte pour
# permettre d'exécuter les migrations contre une DB jetable sans monkeypatch
# sur l'environnement.
_configured_url = config.get_main_option("sqlalchemy.url")
# Le placeholder par défaut dans ``alembic.ini`` est un commentaire
# (``sqlalchemy.url = # ...``) que ConfigParser stocke tel quel. On le
# détecte pour fallback sur les settings de l'application.
if not _configured_url or _configured_url.strip().startswith("#"):
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

    # NullPool pour l'isolation : chaque migration ouvre/ferme sa propre
    # connexion. Les kwargs engine viennent de ``make_engine`` (pas de
    # duplication avec ``db.py``).
    connectable = make_engine(config.get_main_option("sqlalchemy.url"), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
