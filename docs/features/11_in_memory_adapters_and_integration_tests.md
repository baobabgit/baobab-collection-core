# Feature 11 — In-memory adapters and integration tests

## Objectif

Fournir des adaptateurs **mémoire** pour les ports de persistance et de journal, et des **tests d’intégration** qui enchaînent services + infra sans I/O externe.

## Finalité

Permettre aux consommateurs et au CI de valider des parcours réalistes (création d’entités, synchro, journal) sans base de données ni réseau.

## Périmètre

- implémentations `infrastructure.memory` (`InMemoryUserRepository`, `InMemoryCardRepository`, `InMemoryPhysicalCopyRepository`, `InMemoryContainerRepository`, `InMemoryLocalMutationJournal`) ;
- tests d’intégration sous `tests/baobab_collection_core/integration/` (parcours multi-services).

## Hors périmètre

- adaptateurs SQL, fichiers ou API distantes ;
- tests de charge ou de fuzzing.

## Critères d’acceptation

- les adaptateurs respectent les contrats des ports ;
- au moins un parcours d’intégration couvre l’usage combiné services + repositories + journal.
