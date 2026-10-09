"""Point d'entrée console : lance le serveur de développement uvicorn.

Usage :
    uv run chess-analyzer
    # équivalent à : uv run uvicorn chess_analyzer.main:app --reload
"""

from __future__ import annotations

import uvicorn


def main() -> None:
    """Démarre uvicorn en mode développement (reload activé)."""

    uvicorn.run("chess_analyzer.main:app", reload=True)


if __name__ == "__main__":
    main()
