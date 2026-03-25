# Journal de développement — baobab-collection-core

Les entrées les plus récentes en premier.

---

## 2026-03-25 (primitives domaine, feature 02)

### Modifications

- Ajout des value objects et enums sous `domain/` (identifiants UUID, version optimiste, horodatages, synchro, cycle de vie).
- `EntityBase` comme point d’extension pour futures entités ; `ValidationException` pour les incohérences.
- Couverture de tests exhaustive sur validations et transitions d’état.

### Buts

- Centraliser les briques partagées avant usager / carte / copie / contenant / mutations.

### Impact

- Features suivantes peuvent composer ces primitives sans dupliquer la modélisation transverse.

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
