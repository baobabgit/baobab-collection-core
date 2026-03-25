# Journal de développement — baobab-collection-core

Les entrées les plus récentes en premier.

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
