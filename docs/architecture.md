# Architecture — baobab-collection-core

Ce document résume l’architecture **réellement implémentée** dans le dépôt (hexagonale / ports-adaptateurs). Il complète le [cahier des charges](01_specifications.md) sans le dupliquer.

À partir de la **1.0.0**, le contrat d’import **stable** pour les consommateurs repose sur les symboles listés dans `__all__` de chaque sous-package (`domain`, `application`, `ports`, `infrastructure`, `exceptions`) ; le `__init__.py` racine demeure intentionnellement minimal (voir [README](../README.md)).

## Vue en couches

```text
┌─────────────────────────────────────────────────────────┐
│  Consommateur (CLI, API, UI — hors dépôt)               │
└───────────────────────────┬─────────────────────────────┘
                            │ appelle
┌───────────────────────────▼─────────────────────────────┐
│  application/                                           │
│  Services : User*, Card*, PhysicalCopy*, Container*, │
│  CollectionBusiness*, MutationTracking*, SyncCore*,   │
│  SyncConflict*                                          │
└───────────────────────────┬─────────────────────────────┘
                            │ dépend de
┌───────────────────────────▼─────────────────────────────┐
│  ports/                                                 │
│  UserRepositoryPort, CardRepositoryPort,              │
│  PhysicalCopyRepositoryPort, ContainerRepositoryPort,   │
│  LocalMutationJournalPort, RemoteEntitySyncSnapshotPort│
└───────────────────────────▲─────────────────────────────┘
                            │ implémenté par
┌───────────────────────────┴─────────────────────────────┐
│  infrastructure/memory/ (référence)                     │
│  autres backends (SQL, fichiers — hors dépôt)           │
└─────────────────────────────────────────────────────────┘
         utilise des types de
┌─────────────────────────────────────────────────────────┐
│  domain/                                                │
│  Entités, value objects, enums synchro / mutations      │
└─────────────────────────────────────────────────────────┘
```

## Principes

- **Dépendances vers l’intérieur** : `application` et `infrastructure` s’appuient sur `domain` ; le domaine ne dépend pas des ports ni de l’infra.
- **Ports** : abstractions stables (`ABC`) pour la persistance et l’instantané distant.
- **Pas de transport dans le cœur** : aucune requête HTTP ni SDK dans `application` / `domain` ; la synchro manipule des DTO et des services purs + port distant optionnel.

## Paquets Python

| Module | Responsabilité |
|--------|----------------|
| `domain` | Modèle métier, invariants, structures de synchro (`sync_dtos`, conflits, états). |
| `application` | Orchestration, cas d’usage, règles transverses (`collection_counting_rules`). |
| `ports` | Contrats d’accès données / pair distant. |
| `infrastructure` | Implémentations ; seul `infrastructure.memory` est fourni ici comme référence. |
| `exceptions` | Hiérarchie d’erreurs (souvent sous-classes de `ValidationException`). |

## Tests

- **Unitaires** : par module, sous `tests/baobab_collection_core/...`.
- **Intégration** : `tests/baobab_collection_core/integration/` avec `IntegrationHarness` (repos mémoire + services).
- **Support** : `tests/.../support/` réexporte les adaptateurs mémoire du package pour compatibilité.

## Fichiers de référence

- Contraintes outillage : [00_dev_constraints.md](00_dev_constraints.md)
- Features numérotées : [features/README.md](features/README.md)
