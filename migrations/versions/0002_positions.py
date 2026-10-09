"""add positions table

Jalon 1 : première table applicative. Une position d'échecs identifiée par
sa chaîne FEN (clé primaire naturelle) avec un timestamp de création.

Revision ID: 0002_positions
Revises: 0001_init_anchor
Create Date: 2026-10-09 23:41:05.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_positions"
down_revision: str | Sequence[str] | None = "0001_init_anchor"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crée la table ``positions`` (FEN PK + created_at)."""

    op.create_table(
        "positions",
        sa.Column("fen", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("fen"),
    )


def downgrade() -> None:
    """Supprime la table ``positions``."""

    op.drop_table("positions")
