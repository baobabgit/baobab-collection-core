# Domaine métier — panorama

Ce document décrit les **concepts métier exposés** par la librairie et leur articulation. Le détail des invariantes se trouve dans le code (`domain/`) et les fiches [features/](features/README.md).

## Acteurs et agrégats

### Usager (`CollectionUser`)

Représente une personne utilisatrice de la collection. Attributs notables : identifiant, nom affiché (unicité insensible à la casse côté service), statut actif/inactif, métadonnées de cycle de vie / synchro.

**Service** : `UserApplicationService` + `UserRepositoryPort`.

### Carte (`CollectionCard`)

Référence catalogue d’une carte possédée : libellé, attributs optionnels (édition, langue, tags, identifiant externe avec détection de doublons normalisée).

**Service** : `CardApplicationService` + `CardRepositoryPort`.

### Exemplaire physique (`PhysicalCopy`)

Instance concrète liée à **une** carte et **un** propriétaire (usager). Porte état matériel (`PhysicalCopyCondition`), statut métier (`PhysicalCopyBusinessStatus`), emplacement (note libre, contenant optionnel), langue/finition, notes. Supporte suppression logique et synchronisation via métadonnées.

**Service** : `PhysicalCopyApplicationService` + `PhysicalCopyRepositoryPort`.

### Contenant (`Container`)

Rangement hiérarchique (`parent_id`, enfants directs). Types via `ContainerKind`. Archives et cycles interdits pour les opérations structurelles pertinentes.

**Service** : `ContainerApplicationService` + `ContainerRepositoryPort`.

## Métadonnées communes

`EntityMetadata` agrège :

- `AuditTimestamps` ;
- `EntityVersion` (numéro entier monotone côté règles métier) ;
- `SyncState` pour le pipeline offline-first.

Les entités mutent via méthodes de domaine qui respectent la monotonie de version là où c’est exigé.

## Règles d’inventaire et de lecture

`CollectionBusinessService` fournit des vues et compteurs :

- cartes distinctes possédées ;
- total d’exemplaires en inventaire (hors suppression logique) ;
- exemplaires « disponibles » (cf. `collection_counting_rules` : statuts `ACTIVE` / `FOR_TRADE`) ;
- contenu d’un contenant (`ContainerInventoryView`) ;
- localisation d’une copie (`CopyLocation`) ;
- signaux de doublons (cartes par `external_id`, copies par signature simple).

Les règles exactes sont **centralisées** dans `application/collection_counting_rules.py` pour éviter les divergences UI / API.

## Mutations locales

`LocalMutation` trace une opération à propager : entité cible (`LocalEntityKind`), type (`LocalMutationKind`), version et `SyncState` au moment de l’enregistrement, charge utile discrète (`payload_hints`).

Le port `LocalMutationJournalPort` est implémenté en mémoire par `InMemoryLocalMutationJournal` ; `MutationTrackingService` expose enregistrement, liste pending, acquittements.

## Liens entre documents

- Contenants et copies : rattachement via `PhysicalCopyApplicationService.attach_container` / `detach_container`.
- Synchronisation des états : voir [synchronization.md](synchronization.md).
