# Journal de développement — baobab-collection-core

Les entrées les plus récentes en premier.

---

## 2026-03-25 (bootstrap projet)

### Modifications

- Ajout du packaging PEP 621 (`pyproject.toml`), layout `src/`, sous-packages domaine / application / ports / infrastructure / exceptions.
- Introduction de `BaobabCollectionCoreException`, `py.typed`, tests pytest + couverture (seuil 90 %).
- Configuration des outils : black, mypy strict, pylint, flake8 (via Flake8-pyproject), bandit, pytest-cov.

### Buts

- Disposer d’un socle immédiatement utilisable pour les features métier décrites dans `docs/features/`.

### Impact

- Installation éditable et exécution des tests possibles dès la livraison ; contraintes de `docs/00_dev_constraints.md` applicables au code nouveau.
