# Changelog

Toutes les modifications notables sont documentées dans ce fichier.

Le format est inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [0.7.0] - 2026-03-25

### Added

- `CollectionBusinessService` : agrégats (cartes distinctes possédées, totaux inventaire,
  exemplaires disponibles), localisation de copie, copies actives par carte, contenu de contenant.
- Règles explicites dans `collection_counting_rules` (inventaire vs disponibilité, exclusions
  des copies supprimées logiquement).
- Détection de doublons simples : entrées catalogue (`external_id`) et signatures de copies
  actives `(carte, propriétaire, langue, finition)`.
- Extensions du port `PhysicalCopyRepositoryPort` : `list_all_physical_copies`,
  `list_by_container_id`.
- Types read-model : `CopyLocation`, `ContainerInventoryView`, `DuplicateCatalogCardGroup`,
  `DuplicateCopySignatureGroup`.

## [0.6.0] - 2026-03-25

### Added

- Entité `Container` et énum `ContainerKind` (hiérarchie parent / enfant, archivage via cycle de vie).
- Port `ContainerRepositoryPort`, `ContainerApplicationService` (création, mise à jour, archivage,
  rattachement, déplacement, liste des enfants directs).
- Exceptions `InvalidContainerException`, `ContainerNotFoundException`, `ContainerCycleException`.
- Détection explicite des cycles lors des changements de parent et tests associés.

## [0.5.0] - 2026-03-25

### Added

- Entité `PhysicalCopy` (exemplaire physique rattaché à une carte et un propriétaire).
- Énums `PhysicalCopyCondition`, `PhysicalCopyBusinessStatus`.
- Port `PhysicalCopyRepositoryPort`, `PhysicalCopyApplicationService` (création, mise à jour,
  transitions d'état, rattachement contenant, suppression logique, liste par carte).
- Exceptions `InvalidPhysicalCopyException`, `PhysicalCopyNotFoundException`.
- Dépôt mémoire de test et jeux de tests domaine / application.

## [0.4.0] - 2026-03-25

### Added

- Entité `CollectionCard` (référence de collection, distincte d'une copie physique).
- Port `CardRepositoryPort` et `CardApplicationService` (create, update, get, list).
- Exceptions `InvalidCardException`, `CardNotFoundException`, `DuplicateCardException`.
- Dépôt mémoire de test et jeux de tests domaine / application.

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
