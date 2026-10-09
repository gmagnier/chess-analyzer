"""Anchor revision (vide).

Jalon 0 : aucune table applicative n'est encore définie. Cette révision sert
de point d'entrée à la chaîne de migrations Alembic et garantit qu'
``alembic upgrade head`` crée bien le fichier SQLite.

Les modèles métier (positions, parties, répertoire, ...) seront introduits
dans les jalons suivants via de nouvelles révisions.
"""

from __future__ import annotations

# revision identifiers, used by Alembic.
revision = "0001_init_anchor"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Schéma initial vide — ancêtre de la chaîne de migrations."""

    pass


def downgrade() -> None:
    """Revenir à l'état d'avant cette révision (aucun schéma à défaire)."""

    pass