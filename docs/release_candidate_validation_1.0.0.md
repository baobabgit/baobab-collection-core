# Validation release candidate 1.0.0

Journal d’exécution (reproductible) pour une publication PyPI immédiate.  
Date de la passe : **2026-03-25**. Environnement : Windows, Python **3.13.12** (venv projet `.venv`).

## 1. Contrôles qualité (depuis la racine du dépôt)

| Commande | Résultat |
|----------|----------|
| `python -m black --check src tests` | OK — *120 files would be left unchanged* |
| `python -m mypy src tests` | OK — *Success: no issues found in 120 source files* |
| `python -m flake8 src tests` | OK — aucune sortie |
| `python -m bandit -q -c pyproject.toml -r src` | OK — aucune alerte (hors skips projet, ex. B101) |
| `python -m pylint -j 0 --recursive=y src tests` | OK — note **10.00/10** |
| `python -m pytest` | OK — **197 passed** ; couverture totale **95,97 %** ; seuil `fail_under = 90` respecté |

Les tests incluent les parcours marqués `integration` (ex. `tests/baobab_collection_core/integration/`).

## 2. Artefacts de distribution

| Commande | Résultat |
|----------|----------|
| `python -m pip install "build>=1.0.0,<2.0"` | Outil `build` disponible (également listé dans `[project.optional-dependencies].dev`) |
| `python -m build --sdist --wheel` | OK — `dist/baobab_collection_core-1.0.0.tar.gz` et `dist/baobab_collection_core-1.0.0-py3-none-any.whl` |

Vérifications wheel : présence de `baobab_collection_core/py.typed` et de `*.dist-info/METADATA`.

## 3. Installation dans des environnements propres

Deux venv locaux ignorés par git (`.rc-test-venv/`, `.rc-test-venv-sdist/`) :

1. **Wheel** : `pip install dist/baobab_collection_core-1.0.0-py3-none-any.whl`  
   - `from baobab_collection_core import __version__` → `1.0.0`  
   - Scénario minimal : `UserApplicationService` + `InMemoryUserRepository`, `create_user` / `get_user_by_id`.

2. **sdist** : `pip install dist/baobab_collection_core-1.0.0.tar.gz`  
   - `__version__` → `1.0.0`

## 4. Cohérence PyPI (aperçu)

- **Nom / version** : `baobab-collection-core` **1.0.0** (`pyproject.toml`).
- **README** : référencé par `readme = "README.md"` (contenu dans les métadonnées du wheel).
- **Licence** : MIT (fichier `LICENSE` inclus dans les artefacts).
- **Typage** : classifier `Typing :: Typed` + fichier `py.typed` empaqueté.
- **Classifier statut** : `Development Status :: 5 - Production/Stable`.

## 5. Points de vigilance

- **Bandit** : la configuration projet ignore le répertoire `tests/` et applique `skips = ["B101"]` (assert utilisés dans les tests — acceptable pour cette lib).
- **Artefacts `dist/`** : répertoire gitignore ; regénérer avant publication avec `python -m build --sdist --wheel`.
