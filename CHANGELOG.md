# Changelog

Toutes les modifications notables sont documentées dans ce fichier.

Le format est inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [0.3.0] - 2026-03-25

### Added

- Entité `CollectionUser` (nom affiché, actif/inactif, métadonnées / synchro / version).
- Port `UserRepositoryPort` et service applicatif `UserApplicationService` (CRUD logique de base + liste).
- Exceptions `InvalidUserException`, `UserNotFoundException`, `DuplicateUserException`.
- Tests domaine + applicatifs ; dépôt mémoire de test sous `tests/.../support/`.

## [0.2.0] - 2026-03-25

### Added

- Primitives de domaine : `DomainId`, `EntityVersion`, `AuditTimestamps`, `EntityMetadata`, `EntityBase`.
- Énums `SyncState` et `EntityLifecycleState`.
- Exception `ValidationException` pour les règles de validation projet.
- Tests unitaires associés (couverture maintenue).

## [0.1.0] - 2026-03-25

### Added

- Structure `src/` avec package `baobab_collection_core` (sous-packages `domain`, `application`, `ports`, `infrastructure`, `exceptions`).
- Exception racine `BaobabCollectionCoreException` et marqueur `py.typed`.
- Configuration centralisée dans `pyproject.toml` : build, outils qualité (black, mypy, pylint, flake8, bandit, pytest, coverage).
- Tests initiaux d’import et de l’exception racine.
- Documentation de base : `README.md`, journal `docs/dev_diary.md`, fiches sous `docs/features/`.
