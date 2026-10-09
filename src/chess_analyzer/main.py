"""Entrée HTTP FastAPI du squelette.

Expose deux routes minimales :
- ``GET /`` : page d'accueil HTML statique.
- ``GET /healthz`` : JSON ``{"status": "ok"}`` (sondes de vie).

Aucun code métier ; la brique persistance est câblée via ``get_db`` mais
n'est pas encore consommée (modèles à venir aux jalons suivants).
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from chess_analyzer.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)


_HTML_INDEX = """<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <title>chess-analyzer</title>
  </head>
  <body>
    <main>
      <h1>chess-analyzer</h1>
      <p>Squelette du projet en place. Endpoint de sant&eacute; :
        <a href="/healthz">/healthz</a>.</p>
    </main>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root() -> HTMLResponse:
    """Page d'accueil HTML statique."""

    return HTMLResponse(content=_HTML_INDEX)


# Variante HEAD : renvoyée par les sondes Kubernetes/ALB qui utilisent HEAD
# par défaut. FastAPI ne déduit pas HEAD depuis GET, d'où le doublon.
@app.head("/", include_in_schema=False)
async def root_head() -> HTMLResponse:
    """Variante HEAD de la racine (sondes probe-friendly)."""

    return HTMLResponse(content=_HTML_INDEX)


@app.get("/healthz", response_class=JSONResponse)
async def healthz() -> JSONResponse:
    """Sonde de vie : renvoie ``{"status": "ok"}``."""

    return JSONResponse({"status": "ok"})


@app.head("/healthz")
async def healthz_head() -> JSONResponse:
    """Variante HEAD de la sonde de vie (sondes probe-friendly)."""

    return JSONResponse({"status": "ok"})
