# baobab-collection-core

Bibliothèque Python **typed** : noyau de domaine pour la gestion de collections (cartes, exemplaires physiques, conteneurs, synchronisation *offline-first*, etc.). Ce dépôt est en phase de fondations ; la logique métier détaillée arrive dans les features suivantes.

## Prérequis

- Python **3.11** ou supérieur.

## Installation (développement)

```bash
python -m pip install -e ".[dev]"
```

## Utilisation minimale

```python
from baobab_collection_core import BaobabCollectionCoreException

raise BaobabCollectionCoreException("exemple d'erreur projet")
```

## Qualité et tests

Après `pip install -e ".[dev]"` :

```bash
pytest
black src tests
mypy src tests
pylint src tests
flake8 src tests
bandit -c pyproject.toml -r src
```

La couverture est configurée pour viser **90 %** minimum (seuil `fail_under` dans `pyproject.toml`). Les artefacts HTML/XML sont générés sous `docs/tests/coverage/`.

## Structure du code

- `src/baobab_collection_core/` — package installable (`domain`, `application`, `ports`, `infrastructure`, `exceptions`).
- `tests/` — tests miroir de l’arborescence du package.
- `docs/` — contraintes, spécifications, journal de développement, fiches features.

## Contribution

1. Créer une branche depuis `main` (ex. `feature/…` ou `fix/…`).
2. Respecter `docs/00_dev_constraints.md`.
3. Vérifier tests, typage, formatage et lint avant PR.

Les messages de commit suivent **Conventional Commits** (voir les contraintes du projet).

## Licence

Distribué sous licence MIT — voir le fichier [LICENSE](LICENSE).
