"""chess-analyzer — package racine.

Squelette minimal (Jalon 0) : app FastAPI (routes ``async def``, mais
moteur SQLAlchemy **synchrone** câblé via ``get_db`` — voir db.py),
configuration via pydantic-settings, persistance SQLite via SQLAlchemy 2.x
et Alembic. Aucun code métier à ce stade.
"""

__version__ = "0.0.0"
