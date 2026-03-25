# Checklist de release — baobab-collection-core

Liste opérationnelle **avant** de taguer ou publier une version (PyPI ou dépôt privé). Aucune étape ci-dessous ne déclenche de publication automatique.

## Code et API

- [ ] `pyproject.toml` : version **SemVer** cohérente avec [CHANGELOG.md](../CHANGELOG.md).
- [ ] Classifiers PyPI : pour une release stable, `Development Status :: 5 - Production/Stable` (ou équivalent) cohérent avec la politique produit.
- [ ] `baobab_collection_core.__version__` : repli aligné avec la version cible si le package n’est pas installé depuis une wheel/sdist (voir `__init__.py`).
- [ ] `tests/baobab_collection_core/test_package.py` : assertion de repli `__version__` mise à jour.
- [ ] Surface à la racine : uniquement les symboles documentés (`__all__` du `__init__.py` racine).
- [ ] Pas de régression API documentée dans le README sans entrée CHANGELOG (ou version **major** / section **Breaking**).

## Qualité

- [ ] `pytest` — totalité des tests, couverture **≥ seuil** (`fail_under` dans `pyproject.toml`).
- [ ] `black src tests` — aucun reformattage nécessaire.
- [ ] `mypy src tests` — succès.
- [ ] `pylint src tests` — objectif habituel 10/10 ou exceptions documentées.
- [ ] `flake8 src tests` — succès.
- [ ] `bandit -c pyproject.toml -r src` — succès.

## Documentation

- [ ] [README.md](../README.md) à jour (installation, concepts, exemples, liens `docs/`).
- [ ] [CHANGELOG.md](../CHANGELOG.md) : section pour la version avec date et catégories (Added/Changed/Fixed/Removed).
- [ ] Guides [architecture.md](architecture.md), [business_domain.md](business_domain.md), [synchronization.md](synchronization.md) cohérents avec le code.
- [ ] [features/README.md](features/README.md) : index des fiches à jour.

## Distribution (manuelle)

- [ ] `python -m build` (ou outil équivalent) produit sdist/wheel valides.
- [ ] Installation test dans un venv propre : `pip install dist/...whl`.
- [ ] Vérification import : `import baobab_collection_core` et chemins documentés.

## Communication

- [ ] Journal [dev_diary.md](dev_diary.md) complété si le projet l’exige.
- [ ] PR / notes de version pour les consommateurs internes.

## Post-release (optionnel)

- [ ] Tag Git `vX.Y.Z` sur le commit de release.
- [ ] Publication PyPI / registre privé selon politique Baobab.
