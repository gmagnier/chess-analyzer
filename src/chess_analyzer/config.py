"""Configuration applicative via pydantic-settings.

Les valeurs sont surchargeables par variables d'environnement (préfixe
``CHESS_ANALYZER_``) ou par un fichier ``.env`` à la racine du dépôt.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres runtime de l'application."""

    model_config = SettingsConfigDict(
        env_prefix="CHESS_ANALYZER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Chemin SQLite par défaut, relatif à la racine du dépôt.
    database_url: str = Field(
        default="sqlite:///./data/chess_analyzer.db",
        description="URL SQLAlchemy de la base de données.",
    )

    app_name: str = Field(
        default="chess-analyzer",
        description="Nom affiché par l'API (titre OpenAPI).",
    )


def get_settings() -> Settings:
    """Retourne une instance ``Settings`` (singleton par import)."""

    return Settings()
