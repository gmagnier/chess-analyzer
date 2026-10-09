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