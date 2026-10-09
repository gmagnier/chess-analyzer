"""Modèle SQLAlchemy pour la table ``positions``.

Une position d'échecs indexée par sa chaîne FEN (clé naturelle). La même
position atteinte par des coups différents partage la même row, ce qui
gère les transpositions nativement et prépare le terrain pour le tracking
de répertoire des jalons suivants.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from chess_analyzer.db import Base


class Position(Base):
    """Position d'échecs identifiée par sa FEN (clé primaire naturelle)."""

    __tablename__ = "positions"

    fen: Mapped[str] = mapped_column(String(120), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
