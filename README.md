# chess-analyzer

## Workflow de développement

| Branche | Rôle | Accès |
| --- | --- | --- |
| `main` | Stable / release | Push direct interdit — PR obligatoire depuis `develop` |
| `develop` | Intégration | Push direct interdit — PR obligatoire depuis une branche de feature |
| `feature/*` | Travail au quotidien | Push libre depuis les forks |

Boucle : `main` ← PR ← `develop` ← PR ← `feature/xxx`.

```bash
git switch develop && git pull
git switch -c feature/my-change
# ... travail ...
git push -u origin feature/my-change
gh pr create --base develop
# après validation, ouvrir la PR develop -> main
```

Règles appliquées sur `main` et `develop` (GitHub Rulesets) :

- PR obligatoire, aucune suppression de branche, pas de force-push
- Squash merge uniquement (historique linéaire), auto-merge activé
- Suppression automatique de la branche après merge
- Résolution des threads de review exigée avant merge

### Commits

Conventional Commits : `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.

### outillage

- `.github/pull_request_template.md` — checklist de PR
- `.github/dependabot.yml` — mises à jour des GitHub Actions

## Quickstart

Pré-requis : [uv](https://docs.astral.sh/uv/) ≥ 0.5 et Python ≥ 3.12 (uv le
prend en charge automatiquement via le fichier `uv.lock`).

```bash
uv sync --all-extras           # crée .venv et installe runtime + dev
uv run alembic upgrade head    # crée data/chess_analyzer.db (révision vide d'amorçage)
uv run uvicorn chess_analyzer.main:app    # sert http://127.0.0.1:8000
uv run pytest -q                # 2 tests verts (squelette)
```

Endpoints exposés par le squelette :

- `GET /` — page d'accueil HTML statique.
- `GET /healthz` — sonde de vie JSON (`{"status":"ok"}`).

### Statut Jalon 0

✅ **Squelette projet en place** : layout `src/`, app FastAPI minimale,
SQLite via SQLAlchemy 2.x + Alembic (révision vide d'amorçage), 2 tests
pytest, CI GitHub Actions (ruff check + ruff format + pytest) et
gestionnaire `uv` de bout en bout. Aucun code métier : le répertoire, la
sync Lichess, Stockfish et l'analyse de parties arrivent aux jalons
suivants.
