# Journal de développement — baobab-collection-core

Les entrées les plus récentes en premier.

---

## 2026-03-26 (release stable v1.0.0 — packaging et documentation)

### Modifications

- Version **1.0.0**, classifier PyPI **Production/Stable** dans `pyproject.toml` (aucune entrée
  *Pre-Alpha* résiduelle côté manifeste).
- README (contrat d’API, mention explicite du classifier), **CHANGELOG** 1.0.0 enrichi
  (périmètre, contrat public), spécification §24, fiches `docs/features/12`, repli `__version__`.
- Contrat d’API racine explicite ; docstring `SyncPlanAction.REPORT_CONFLICT` corrigée
  (livraisons précédentes sur la même baseline).

### Buts

- Base SemVer exploitable par les consommateurs, statut stable cohérent dans tout le dépôt
  (hors historique 0.x du CHANGELOG et mentions explicatives).

---

## 2026-03-25 (checklist release v1.0.0 — exécution intégrale)

### Modifications

- Journal factuel [release_checklist_execution_1.0.0.md](release_checklist_execution_1.0.0.md) ;
  renvoi depuis [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).
- Fiche [features/11_in_memory_adapters_and_integration_tests.md](features/11_in_memory_adapters_and_integration_tests.md)
  complétée (n’était plus vide).
- README : mention de l’outil `build` dans l’extra `dev` ; `.gitignore` : `.rc-checklist-venv/`.

### Buts

- Prouver par des commandes réelles que la **v1.0.0** est prête à être taguée / publiée selon la checklist.

---

## 2026-03-25 (documentation & préparation release, feature 12)

### Modifications

- README structuré (objectifs, installation, concepts, offline-first, synchro, exemples, qualité,
  versioning) ; nouveaux documents `docs/architecture.md`, `business_domain.md`,
  `synchronization.md`, index des features, `RELEASE_CHECKLIST.md`.

### Buts

- Rendre le dépôt auditable et utilisable par un intégrateur sans fouiller tout le code.

### Impact

- Version **0.12.0** ; pas de publication PyPI dans cette livraison.

---

## 2026-03-25 (adaptateurs mémoire + intégration, feature 11)

### Modifications

- Emplacement canonique des adaptateurs sous `infrastructure.memory` ; suite d'intégration
  couvrant création entités, inventaire, journal, synchro et conflit simulé.

### Buts

- Référence de comportement des ports et garde-fous de non-régression sur flux métier.

### Impact

- Les applications de démo ou tests externes peuvent importer les adaptateurs depuis le package.

---

## 2026-03-25 (conflits sync, feature 10)

### Modifications

- `SyncConflictDetector`, stratégies de résolution et `SyncConflictResolutionService` ; extension
  des DTO d'instantanés (parent, empreinte, clé externe).

### Buts

- Détecter et résoudre les divergences local / distant sans UI ni backend ; compléter le cœur sync (09).

### Impact

- Les orchestrateurs peuvent brancher des politiques métier ou une future fusion tout en restant testables en mémoire.

---

## 2026-03-25 (abstractions sync cœur, feature 09)

### Modifications

- `SyncCoreService`, DTO de comparaison/plan/résultat, port `RemoteEntitySyncSnapshotPort`.

### Buts

- Préparer synchro local/distant sans HTTP ni backend ; ouvrir la voie à la résolution de conflits (feature 10).

### Impact

- Les orchestrateurs pourront brancher un adaptateur réel sur le port distant et réutiliser plans et agrégats.

---

## 2026-03-25 (mutations locales offline-first, feature 08)

### Modifications

- Introduction de `LocalMutation` et d'un journal porté par `LocalMutationJournalPort` ;
  `MutationTrackingService` pour tracer les changements en attente sans transport réseau.

### Buts

- Compléter les `SyncState` / `EntityMetadata` des agrégats avec une piste d'audit exploitable
  par une synchro ultérieure.

### Impact

- Les services métier existants peuvent appeler le tracking après mutation ; pas d'event sourcing
  complet ni de client HTTP dans ce package.

---

## 2026-03-25 (services métier collection, feature 07)

### Modifications

- `CollectionBusinessService` et règles `collection_counting_rules` ; extensions du port des copies
  pour agrégats et contenu par contenant.

### Buts

- Indicateurs lisibles (inventaire vs disponibilité) sans couche de reporting lourde.

### Impact

- CLI / UI / API pourront s'appuyer sur un contrat stable de read models légers.

---

## 2026-03-25 (contenants, feature 06)

### Modifications

- Ajout de `Container` (`ContainerKind`, parent optionnel, archivage) et du service applicatif
  avec prévention de cycle sur la hiérarchie (remontée d'ancêtres).

### Buts

- Organiser le rangement sans incohérence structurelle ; rester compatible avec `container_id`
  sur les copies physiques.

### Impact

- Navigation avancée et règles sur contenu non vide pourront s'ajouter sans casser le modèle.

---

## 2026-03-25 (copies physiques, feature 05)

### Modifications

- Ajout de `PhysicalCopy` (carte, propriétaire, contenant optionnel, descripteurs, état matériel,
  statut métier, métadonnées / synch / soft delete).
- Port et service applicatif ; exceptions dédiées ; adapter mémoire et tests.

### Buts

- Distinct de la référence carte : plusieurs exemplaires par carte, prêts pour la synch
  offline-first.

### Impact

- Les conteneurs pourront être rattachés sans logique de navigation avancée pour l'instant.

---

## 2026-03-25 (cartes possédées, feature 04)

### Modifications

- Ajout de `CollectionCard` avec identifiants interne/externe, attributs descriptifs, tags et métadonnées.
- Port `CardRepositoryPort`, service applicatif, exceptions dédiées, adapter mémoire de test.

### Buts

- Modéliser la référence carte (agrégat) séparément des exemplaires physiques à venir.

### Impact

- Les copies physiques pourront référencer `entity_id` comme pivot sans fusionner les concepts.

---

## 2026-03-25 (usagers, feature 03)

### Modifications

- Introduction de `CollectionUser`, du port `UserRepositoryPort` et du service `UserApplicationService`.
- Exceptions dédiées (validation, absence, doublon de nom affiché) et dépôt mémoire pour les tests applicatifs.

### Buts

- Couvrir création, mise à jour, désactivation, lecture et liste sans stockage concret dans le package.

### Impact

- Les features « collection » pourront référencer des usagers via un contrat stable.

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
