# baobab-collection-core

Bibliothèque Python **typée** (`py.typed`) : **noyau métier** pour la gestion de collections de cartes, d’exemplaires physiques, de contenants et d’usagers, avec une approche **offline-first** et des abstractions de **synchronisation** sans transport réseau imposé.

> **Version 1.0.0** — Release stable. Compatibilité suivie selon [SemVer](https://semver.org/lang/fr/) : changements incompatibles réservés aux versions **majeures** ; les sous-modules exposés via `__all__` constituent le contrat d’import stable.

Le manifeste du package (`pyproject.toml`) déclare notamment le classifier PyPI **`Development Status :: 5 - Production/Stable`** et `version = "1.0.0"`, en phase avec cette documentation.

## Description et objectifs

Le projet fournit :

- un **modèle de domaine** (entités, invariants, valeur objets) ;
- une **couche application** (cas d’usage : création, mise à jour, inventaire, journal local, synchro logique) ;
- des **ports** (interfaces de persistance et d’instantanés distants) ;
- des **adaptateurs mémoire** de référence pour tests et prototypage ;
- des **exceptions métier** homogènes.

Il **n’inclut pas** d’UI, de serveur HTTP ni de base de données concrète : ces aspects sont laissés aux applications consommatrices.

## Prérequis

- Python **3.11**, **3.12** ou **3.13** (`requires-python >= 3.11`).

## Installation

### Dépendances runtime

Le package **n’a pas de dépendances obligatoires** (stdlib + domaine pur).

### Installation en mode développement

```bash
python -m pip install -e ".[dev]"
```

Le extra `dev` ajoute outils de qualité : `pytest`, `pytest-cov`, `black`, `mypy`, `pylint`, `flake8`, `bandit`, `build` (artefacts sdist/wheel).

### Utilisation comme dépendance (sans publication ici)

Après build local ou publication future sur un index de paquets :

```bash
python -m pip install baobab-collection-core
```

*(Cette commande est illustrative ; le dépôt ne publie pas automatiquement sur PyPI.)*

## Structure du dépôt

| Chemin | Rôle |
|--------|------|
| `src/baobab_collection_core/` | Code installable |
| `src/baobab_collection_core/domain/` | Entités et règles métier |
| `src/baobab_collection_core/application/` | Services applicatifs |
| `src/baobab_collection_core/ports/` | Contrats (repositories, journal, instantané distant) |
| `src/baobab_collection_core/infrastructure/` | Implémentations techniques (ex. `infrastructure.memory`) |
| `src/baobab_collection_core/exceptions/` | Erreurs projet |
| `tests/` | Tests unitaires, d’intégration (`tests/.../integration/`), support |
| `docs/` | Spécifications, contraintes, architecture, domaine, synchro, fiches features |

Documentation détaillée : [Architecture](docs/architecture.md), [Domaine métier](docs/business_domain.md), [Synchronisation](docs/synchronization.md), [Index des features](docs/features/README.md).

## Concepts métier principaux

- **Usager** (`CollectionUser`) : personne associée à la collection.
- **Carte** (`CollectionCard`) : référence catalogue (nom, identifiants externes optionnels, etc.).
- **Exemplaire physique** (`PhysicalCopy`) : copie concrète liée à une carte et un propriétaire ; état matériel, statut métier, rattachement optionnel à un contenant.
- **Contenant** (`Container`) : rangement hiérarchique (parent/enfants, pas de cycles).
- **Métadonnées transverses** (`EntityMetadata`, `EntityVersion`, `SyncState`, horodatage) : version optimiste et cycle de synchro.
- **Mutations locales** (`LocalMutation`) : journal offline-first des opérations à propager.

Règles d’agrégats et de comptage (inventaire vs disponibilité) : module `collection_counting_rules` et `CollectionBusinessService`.

## Offline-first

Les entités portent un `SyncState` (`clean`, `dirty`, `synced`, `conflict`, `sync_error`, `deleted`). Les créations et mises à jour typiques passent par les services applicatifs qui positionnent l’état pour refléter un travail local en attente de propagation.

Le **`MutationTrackingService`** enregistre des entrées dans un **`LocalMutationJournalPort`** (append + remplacement pour accusés), avec extraction des changements **pending** et méthodes d’acquittement.

## Synchronisation

La synchro est modélisée **sans HTTP** :

- **`SyncCoreService`** : compare instantanés locaux/distant (`LocalEntitySyncSnapshot`, `RemoteEntitySyncSnapshot`), produit des **deltas**, un **plan** (`SyncPlan`), consolide des **résultats de lot**, applique des **`SyncSessionOutcome`** sur `EntityMetadata`.
- **`RemoteEntitySyncSnapshotPort`** : point d’extension pour fournir l’état distant (implémentations tests/adapter réels).
- **Conflits** : **`SyncConflictDetector`**, modèle **`SyncConflict`** / **`SyncConflictKind`**, stratégies injectables **`SyncConflictResolutionStrategy`** (local prioritaire, distant prioritaire, manuel explicite) et **`SyncConflictResolutionService`**.

Voir [docs/synchronization.md](docs/synchronization.md).

## Exemples d’usage

### Créer un usager (service + dépôt mémoire)

```python
from datetime import datetime, timezone

from baobab_collection_core.application.user_application_service import UserApplicationService
from baobab_collection_core.infrastructure.memory import InMemoryUserRepository

moment = datetime.now(timezone.utc)
users = InMemoryUserRepository()
app = UserApplicationService(users)
user = app.create_user("Alice", moment)
print(user.entity_id, user.display_name)
```

### Inventaire agrégé (cartes, copies, contenants)

```python
from baobab_collection_core.application.collection_business_service import CollectionBusinessService
from baobab_collection_core.infrastructure.memory import (
    InMemoryCardRepository,
    InMemoryContainerRepository,
    InMemoryPhysicalCopyRepository,
)

business = CollectionBusinessService(
    InMemoryCardRepository(),
    InMemoryPhysicalCopyRepository(),
    InMemoryContainerRepository(),
)
print(business.count_distinct_cards_in_collection())
```

### Comparer local / distant (cœur de synchro)

```python
from baobab_collection_core.application.sync_core_service import SyncCoreService
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.sync_dtos import LocalEntitySyncSnapshot, RemoteEntitySyncSnapshot
from baobab_collection_core.domain.sync_state import SyncState

eid = DomainId("550e8400-e29b-41d4-a716-446655440000")  # exemple
local = LocalEntitySyncSnapshot(
    entity_id=eid,
    entity_kind=LocalEntityKind.COLLECTION_USER,
    version=1,
    sync_state=SyncState.DIRTY,
    is_logically_deleted=False,
)
remote = RemoteEntitySyncSnapshot(
    entity_id=eid,
    present=True,
    version=3,
    is_logically_deleted=False,
)
delta = SyncCoreService().compare(local, remote)
print(delta.kind)
```

### API publique du package racine

Le package expose volontairement peu de symboles à la racine (`__init__.py`) : **`BaobabCollectionCoreException`** et **`__version__`**. Importez les classes métier depuis leurs sous-modules (comme ci-dessus).

## Tests d’intégration

Une harness mémoire et des scénarios bout-en-bout sont dans `tests/baobab_collection_core/integration/` (marqueur pytest `integration`). Le jeu complet de tests inclut couverture avec seuil **90 %** :

```bash
pytest
```

Pour lancer uniquement les tests d’intégration (sans viser le seuil de couverture global, selon la configuration locale) :

```bash
pytest -m integration --no-cov
```

## Qualité (locale)

Après `pip install -e ".[dev]"` :

```bash
black src tests
mypy src tests
pylint src tests
flake8 src tests
bandit -c pyproject.toml -r src
pytest
```

Rapports de couverture : `docs/tests/coverage/html/` et `coverage.xml`.

## Versioning

- À partir de **1.0.0**, le projet suit [SemVer](https://semver.org/lang/fr/) : **MAJEUR** pour ruptures d’API documentées, **MINEUR** pour ajouts rétrocompatibles, **PATCH** pour corrections.
- L’historique détaillé est dans [CHANGELOG.md](CHANGELOG.md).
- La version canonique est `pyproject.toml` ; `baobab_collection_core.__version__` lit les métadonnées d’installation ou une **repli** alignée sur cette version.

Checklist avant une prochaine release : [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md).  
Publication **v1.0.0** (GitHub Release, tag `v1.0.0`, PyPI) : [docs/release_v1.0.0_publishing.md](docs/release_v1.0.0_publishing.md).

## Contribution

1. Branche depuis `main` (ex. `feature/…`, `fix/…`).
2. Respecter [docs/00_dev_constraints.md](docs/00_dev_constraints.md) (structure, tests, qualité, Git, journal optionnel).
3. Mettre à jour le [CHANGELOG.md](CHANGELOG.md) pour les modifications notables.
4. Vérifier tests, typage, formatage et lint avant ouverture de PR.

Messages de commit : style **Conventional Commits** (voir contraintes projet).

## Documentation complémentaire

- [Cahier des charges](docs/01_specifications.md)
- [Contraintes de développement](docs/00_dev_constraints.md)
- [Journal de développement](docs/dev_diary.md)
- [Publication v1.0.0 (GitHub / PyPI)](docs/release_v1.0.0_publishing.md)

## Licence

MIT — voir [LICENSE](LICENSE).
