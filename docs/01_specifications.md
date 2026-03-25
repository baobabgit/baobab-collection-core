# Cahier des charges — baobab-collection-core

## 1. Présentation du projet

### 1.1 Nom
`baobab-collection-core`

### 1.2 Nature du projet
Librairie Python orientée domaine métier dédiée à la gestion d’une collection de cartes, de leurs copies physiques, de leurs contenants et des usagers, avec un fonctionnement **offline-first** et une **synchronisation local / distant**.

### 1.3 Finalité
La librairie doit fournir un cœur métier réutilisable, indépendant d’une interface utilisateur donnée, permettant de construire par-dessus :
- une application CLI ;
- une application desktop ;
- une API ;
- un service local ;
- une application mobile ou web via un adaptateur.

### 1.4 Objectif principal
Créer une base métier robuste, testée, typée et extensible pour modéliser une collection de cartes physiques, manipuler les entités de collection même hors ligne, puis synchroniser l’état local avec un stockage distant.

---

## 2. Objectifs fonctionnels

La librairie doit couvrir les responsabilités suivantes :

- gestion des usagers ;
- gestion des cartes possédées ;
- gestion des copies physiques ;
- gestion des contenants ;
- logique métier de collection ;
- fonctionnement offline-first ;
- synchronisation local / distant.

---

## 3. Périmètre fonctionnel

### 3.1 Inclus
Le périmètre de la librairie inclut :

- le modèle métier des entités de collection ;
- les règles métier associées ;
- les opérations CRUD métier ;
- la validation des données métier ;
- la gestion des relations entre cartes, copies, usagers et contenants ;
- la persistance locale via abstraction ;
- la représentation d’un état modifié localement ;
- le suivi des changements à synchroniser ;
- le moteur de synchronisation ;
- la gestion des conflits de synchronisation ;
- les événements métier internes ;
- les abstractions pour brancher différents stockages locaux ou distants ;
- les erreurs métier spécifiques au projet.

### 3.2 Exclus
Le périmètre n’inclut pas :

- une interface graphique ;
- une interface web ;
- une CLI finale ;
- une API HTTP prête à déployer ;
- l’authentification distante complète ;
- l’intégration à une base spécifique imposée ;
- le téléchargement automatique de catalogues de cartes ;
- le scraping de sites externes ;
- une logique spécifique à un jeu particulier, sauf si modélisée de manière générique.

---

## 4. Vision produit

### 4.1 Positionnement
`baobab-collection-core` est un **noyau métier**.  
Il ne doit pas dépendre d’une application finale, mais l’application finale doit pouvoir dépendre de lui.

### 4.2 Principes d’architecture
La librairie doit respecter les principes suivants :

- **domain-first** ;
- **offline-first** ;
- **framework-agnostic** ;
- **fortement typée** ;
- **testable** ;
- **extensible** ;
- **faiblement couplée** ;
- **orientée interfaces / ports / adapters**.

---

## 5. Cas d’usage principaux

### 5.1 Gestion des usagers
- créer un usager ;
- modifier un usager ;
- désactiver un usager ;
- consulter un usager ;
- lister les usagers ;
- rattacher des éléments de collection à un usager ;
- transférer la propriété ou la responsabilité de certains éléments d’un usager à un autre.

### 5.2 Gestion des cartes possédées
- enregistrer qu’un usager possède une carte ;
- distinguer la **carte conceptuelle** de la **copie physique** ;
- agréger plusieurs copies d’une même carte ;
- consulter les informations métier d’une carte possédée ;
- regrouper les cartes par catégories, tags ou états.

### 5.3 Gestion des copies physiques
- créer une copie physique ;
- associer une copie à une carte ;
- associer une copie à un usager ;
- affecter une copie à un contenant ;
- modifier l’état d’une copie ;
- tracer l’historique logique d’une copie ;
- déplacer une copie d’un contenant à un autre ;
- retirer ou archiver une copie.

### 5.4 Gestion des contenants
- créer un contenant ;
- définir un type de contenant ;
- établir une hiérarchie de contenants ;
- déplacer un contenant dans un autre contenant ;
- lister le contenu d’un contenant ;
- calculer des statistiques de contenu ;
- garantir les contraintes de capacité ou de cohérence.

### 5.5 Logique métier de collection
- compter les cartes, copies et contenants ;
- calculer la répartition par usager, catégorie, état, emplacement ;
- retrouver l’emplacement d’une copie ;
- vérifier l’intégrité de la collection ;
- détecter incohérences, doublons ou références invalides ;
- produire des vues métier cohérentes.

### 5.6 Offline-first
- permettre toutes les opérations métier sans connexion ;
- enregistrer localement les modifications ;
- conserver l’état des objets et le journal des changements ;
- marquer les éléments en attente de synchronisation ;
- permettre la consultation locale.

### 5.7 Synchronisation local / distant
- identifier les changements locaux non synchronisés ;
- pousser les changements locaux vers le distant ;
- récupérer les changements distants ;
- résoudre les conflits ;
- marquer les changements comme synchronisés ;
- fournir un rapport de synchronisation détaillé.

---

## 6. Hypothèses métier structurantes

Les hypothèses suivantes structurent la conception initiale :

1. Une **carte** représente une entité logique décrivant un objet collectionnable.
2. Une **copie physique** représente un exemplaire concret de cette carte.
3. Un **usager** représente une personne ou un profil logique propriétaire, gestionnaire ou détenteur.
4. Un **contenant** représente un espace logique ou physique de rangement.
5. Un contenant peut contenir :
   - des copies physiques ;
   - d’autres contenants.
6. Une copie physique ne peut appartenir qu’à **un seul contenant direct** à un instant donné.
7. Une copie physique est rattachée à **une seule carte logique**.
8. Une copie physique peut être rattachée à **un seul usager référent** à un instant donné.
9. Toute modification locale significative doit pouvoir être journalisée en vue d’une synchronisation.
10. La librairie doit rester générique et ne pas imposer un jeu de cartes particulier.

---

## 7. Modèle métier cible

### 7.1 Entités principales

#### User
Représente un usager.

Attributs minimum :
- `user_id`
- `external_id` optionnel
- `display_name`
- `email` optionnel
- `is_active`
- `created_at`
- `updated_at`
- `version`
- `sync_status`

#### Card
Représente une carte logique.

Attributs minimum :
- `card_id`
- `external_id` optionnel
- `name`
- `game_code` optionnel
- `edition` optionnel
- `language` optionnel
- `metadata`
- `created_at`
- `updated_at`
- `version`
- `sync_status`

#### PhysicalCopy
Représente une copie physique d’une carte.

Attributs minimum :
- `copy_id`
- `card_id`
- `owner_user_id` optionnel
- `current_container_id` optionnel
- `condition`
- `is_foil` optionnel
- `is_signed` optionnel
- `purchase_price` optionnel
- `currency` optionnel
- `acquired_at` optionnel
- `notes` optionnel
- `tags`
- `created_at`
- `updated_at`
- `version`
- `sync_status`

#### Container
Représente un contenant logique ou physique.

Attributs minimum :
- `container_id`
- `external_id` optionnel
- `name`
- `container_type`
- `parent_container_id` optionnel
- `owner_user_id` optionnel
- `capacity` optionnel
- `metadata`
- `created_at`
- `updated_at`
- `version`
- `sync_status`

#### ChangeSet / SyncRecord
Représente une modification locale ou distante en attente ou traitée.

Attributs minimum :
- `change_id`
- `entity_type`
- `entity_id`
- `operation_type`
- `payload`
- `origin`
- `occurred_at`
- `status`
- `attempt_count`
- `conflict_data` optionnel

### 7.2 Value Objects recommandés
- `EntityId`
- `Timestamp`
- `SyncStatus`
- `CopyCondition`
- `ContainerType`
- `Ownership`
- `ChangeOrigin`
- `OperationType`
- `ConflictResolutionStrategy`

### 7.3 Énumérations minimales
- `SyncStatus`: `LOCAL_ONLY`, `SYNC_PENDING`, `SYNCED`, `CONFLICT`, `ERROR`
- `OperationType`: `CREATE`, `UPDATE`, `DELETE`, `ARCHIVE`, `MOVE`
- `CopyCondition`: au minimum `MINT`, `NEAR_MINT`, `GOOD`, `PLAYED`, `DAMAGED`
- `ContainerType`: `BOX`, `BINDER`, `DECK`, `SHELF`, `CASE`, `OTHER`

---

## 8. Règles métier obligatoires

### 8.1 Usagers
- un usager doit avoir un identifiant unique ;
- un nom d’affichage est obligatoire ;
- un usager désactivé ne doit pas être supprimé automatiquement ;
- les opérations doivent permettre la conservation de l’historique logique.

### 8.2 Cartes
- une carte logique doit avoir un identifiant unique ;
- le nom est obligatoire ;
- les métadonnées doivent être extensibles ;
- plusieurs copies peuvent référencer une même carte.

### 8.3 Copies physiques
- une copie physique doit référencer une carte existante ;
- une copie physique ne peut avoir qu’un contenant direct actif à un instant donné ;
- une copie physique ne peut être créée avec un identifiant déjà existant ;
- une copie archivée ou supprimée logiquement ne doit plus apparaître dans les vues actives par défaut ;
- tout déplacement de copie doit mettre à jour son historique et son état de synchronisation.

### 8.4 Contenants
- un contenant ne peut pas être son propre parent ;
- un contenant ne peut pas créer une boucle hiérarchique ;
- un contenant peut imposer une capacité maximale ;
- une copie ne peut pas être insérée dans un contenant plein si la capacité est contraignante ;
- un contenant archivé ne doit plus accepter de nouveaux éléments.

### 8.5 Intégrité globale
- toutes les références doivent être vérifiées ;
- aucune relation invalide ne doit être persistée ;
- les agrégats métiers doivent rester cohérents après chaque opération.

---

## 9. Fonctionnalités détaillées

## 9.1 Module usagers
Fonctionnalités attendues :
- création d’usager ;
- modification ;
- activation / désactivation ;
- suppression logique éventuelle ;
- recherche par identifiant ;
- recherche par nom ;
- listing paginable ou filtrable ;
- rattachement des copies et contenants à un usager.

Services attendus :
- `UserService`
- `UserRepository`
- `UserValidator`

## 9.2 Module cartes
Fonctionnalités attendues :
- création d’une carte logique ;
- mise à jour des métadonnées ;
- recherche ;
- récupération des copies liées ;
- vues agrégées par carte.

Services attendus :
- `CardService`
- `CardRepository`
- `CardValidator`

## 9.3 Module copies physiques
Fonctionnalités attendues :
- création ;
- mise à jour ;
- changement d’état ;
- changement d’usager ;
- affectation à un contenant ;
- déplacement ;
- suppression logique / archivage ;
- recherche multi-critères ;
- comptage et regroupement.

Services attendus :
- `PhysicalCopyService`
- `PhysicalCopyRepository`
- `PhysicalCopyValidator`
- `CopyMoveService`

## 9.4 Module contenants
Fonctionnalités attendues :
- création ;
- renommage ;
- hiérarchisation ;
- déplacement ;
- affectation d’un usager ;
- ajout et retrait de copies ;
- calcul de contenu ;
- calcul de charge ;
- contrôle de capacité ;
- navigation arborescente.

Services attendus :
- `ContainerService`
- `ContainerRepository`
- `ContainerValidator`
- `ContainerHierarchyService`

## 9.5 Module logique métier de collection
Fonctionnalités attendues :
- vue globale d’une collection ;
- calcul du nombre de cartes distinctes ;
- calcul du nombre total de copies ;
- inventaire par usager ;
- inventaire par contenant ;
- recherche d’emplacement ;
- contrôles d’intégrité ;
- statistiques métier.

Services attendus :
- `CollectionService`
- `InventoryService`
- `CollectionIntegrityService`
- `CollectionStatisticsService`

## 9.6 Module offline-first
Fonctionnalités attendues :
- persistance locale ;
- journal des changements ;
- lecture locale ;
- écriture locale ;
- marquage des entités modifiées ;
- consultation des changements en attente ;
- reprise après redémarrage.

Services attendus :
- `LocalStore`
- `ChangeLogRepository`
- `PendingChangesService`
- `OfflineUnitOfWork`

## 9.7 Module synchronisation
Fonctionnalités attendues :
- extraction des changements locaux ;
- application vers le distant ;
- récupération des changements distants ;
- réconciliation ;
- résolution des conflits ;
- génération d’un rapport de synchronisation ;
- suivi des échecs et tentatives.

Services attendus :
- `SyncService`
- `SyncEngine`
- `SyncConflictResolver`
- `RemoteStore`
- `SyncReportBuilder`

---

## 10. Exigences d’architecture

### 10.1 Architecture logique
La librairie doit être organisée en couches :

- `domain` : entités, value objects, règles métier, exceptions métier ;
- `application` : services de cas d’usage ;
- `ports` : interfaces de persistance, synchronisation, horloge, identifiants ;
- `infrastructure` : implémentations concrètes locales / distantes ;
- `shared` : utilitaires internes strictement nécessaires.

### 10.2 Architecture recommandée
Approche **Ports & Adapters / Hexagonal Architecture**.

Les dépendances doivent pointer vers le domaine et non l’inverse.

### 10.3 Indépendance technologique
Le cœur métier ne doit pas dépendre directement :
- d’une base SQLite imposée ;
- d’un ORM imposé ;
- d’un framework web ;
- d’une interface CLI ;
- d’un système de sérialisation externe non encapsulé.

---

## 11. Exigences offline-first

### 11.1 Principe
L’utilisateur doit pouvoir :
- lire les données locales ;
- créer, modifier, déplacer, archiver ;
- continuer à travailler sans connexion ;
- retrouver l’état local au redémarrage.

### 11.2 Règles
- toute opération métier locale doit être persistée localement ;
- tout changement devant être synchronisé doit être journalisé ;
- chaque entité doit porter un état de synchronisation ;
- l’échec de synchronisation ne doit pas faire perdre la donnée locale ;
- le système doit être résilient aux interruptions.

---

## 12. Exigences de synchronisation

### 12.1 Objectif
Permettre la synchronisation entre une source locale et une source distante au travers d’interfaces abstraites.

### 12.2 Modes de synchronisation
Le moteur doit pouvoir supporter à terme :
- push local vers distant ;
- pull distant vers local ;
- synchronisation bidirectionnelle.

### 12.3 Gestion des conflits
Le système doit au minimum prévoir :
- détection de conflit de version ;
- détection de modification concurrente ;
- stratégie configurable de résolution.

Stratégies minimales :
- `LAST_WRITE_WINS`
- `LOCAL_WINS`
- `REMOTE_WINS`
- `MANUAL`

### 12.4 Rapport de synchronisation
Chaque synchronisation doit pouvoir produire :
- nombre d’éléments lus ;
- nombre d’éléments créés ;
- nombre d’éléments mis à jour ;
- nombre d’éléments ignorés ;
- nombre de conflits ;
- nombre d’erreurs ;
- détail par entité si nécessaire.

---

## 13. Exigences de persistance

### 13.1 Persistance locale
La persistance locale doit être abstraite derrière des interfaces.

Une première implémentation peut être prévue ensuite, par exemple :
- mémoire pour les tests ;
- SQLite ;
- fichiers JSON ;
- autre backend local.

### 13.2 Persistance distante
La persistance distante doit être abstraite derrière des interfaces.

Une implémentation distante pourra être branchée plus tard :
- API REST ;
- base distante ;
- service cloud ;
- synchronisation de fichiers.

### 13.3 Contraintes
- aucune implémentation ne doit être imposée au domaine ;
- les sérialisations doivent être maîtrisées ;
- les opérations doivent être atomiques autant que possible ;
- les erreurs d’infrastructure doivent être remontées proprement via des exceptions projet.

---

## 14. API publique de la librairie

### 14.1 Exigence générale
L’API publique doit être claire, stable et orientée usage métier.

### 14.2 Exigences
- exposer des services applicatifs explicites ;
- limiter l’exposition des détails d’infrastructure ;
- documenter tous les points d’entrée publics ;
- garantir des signatures fortement typées ;
- éviter les effets de bord implicites.

### 14.3 Conventions
- méthodes orientées métier ;
- retours explicites ;
- exceptions spécifiques ;
- objets de résultat pour les opérations complexes.

---

## 15. Gestion des erreurs

### 15.1 Principe
Toutes les erreurs spécifiques au projet doivent être représentées par des exceptions dédiées.

### 15.2 Hiérarchie minimale
- `BaobabCollectionCoreException`
- `ValidationException`
- `EntityNotFoundException`
- `ConflictException`
- `SynchronizationException`
- `StorageException`
- `IntegrityException`
- `OfflineStateException`
- `ContainerCapacityException`
- `HierarchyCycleException`

### 15.3 Exigences
- toute exception métier doit hériter de l’exception racine du projet ;
- les exceptions doivent être organisées par domaine ;
- les messages doivent être explicites et exploitables ;
- les erreurs d’infrastructure doivent être encapsulées.

---

## 16. Performance et robustesse

### 16.1 Performance
La librairie doit rester performante sur des volumes courants de collection.

Cibles initiales recommandées :
- navigation fluide sur plusieurs milliers de copies ;
- opérations CRUD unitaires rapides ;
- synchronisation incrémentale prioritaire sur la resynchronisation complète.

### 16.2 Robustesse
- pas de corruption de données en cas d’échec de synchronisation ;
- reprise possible après interruption ;
- validation stricte avant persistance ;
- cohérence des transactions locales.

---

## 17. Sécurité fonctionnelle

Même si la librairie n’est pas un service exposé directement :
- les validations d’entrée doivent être strictes ;
- les identifiants doivent être correctement gérés ;
- aucune exécution dynamique dangereuse ;
- aucune dépendance inutile à des composants réseau dans le cœur métier ;
- les données sérialisées doivent être contrôlées.

---

## 18. Compatibilité et environnement

### 18.1 Python
La librairie doit cibler une version moderne de Python, recommandée :
- Python `>=3.11`

### 18.2 Compatibilité
La librairie doit être installable :
- en mode editable ;
- en wheel ;
- via `pip`.

---

## 19. Contraintes de développement

Les contraintes suivantes sont obligatoires.

### 19.1 Structure du projet
- code source dans `src/baobab_collection_core`
- tests dans `tests/`
- documentation dans `docs/`

### 19.2 Organisation du code
- programmation orientée classe ;
- une classe par fichier ;
- arborescence logique par catégorie ;
- noms en `snake_case` pour modules ;
- noms en `PascalCase` pour classes.

### 19.3 Type hints
- annotations de type obligatoires partout ;
- configuration `mypy` stricte ;
- aucun fichier ne doit échouer à l’analyse de types.

### 19.4 Qualité
Le projet doit passer sans erreur :
- `black`
- `pylint`
- `mypy`
- `flake8`
- `bandit`

### 19.5 Longueur de ligne
- maximum `100` caractères.

### 19.6 Configuration
Toute la configuration possible doit être centralisée dans `pyproject.toml`.

### 19.7 Tests
- un fichier de tests par classe ;
- une classe de test par classe principale ;
- couverture minimale `90%`.

### 19.8 Coverage
Les fichiers de couverture doivent être générés dans :
- `docs/tests/coverage`

### 19.9 Documentation
- docstrings sur toutes les API publiques ;
- `README.md`
- `CHANGELOG.md`
- `docs/dev_diary.md`

### 19.10 Journal de développement
Le fichier `docs/dev_diary.md` doit consigner les changements par date décroissante avec :
- modifications ;
- buts ;
- impacts.

### 19.11 Git
- workflow par branches ;
- conventional commits ;
- tags SemVer.

---

## 20. Arborescence cible recommandée

```text
src/baobab_collection_core/
├── __init__.py
├── application/
│   ├── services/
│   ├── dto/
│   └── results/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── enums/
│   ├── services/
│   ├── validators/
│   └── exceptions/
├── ports/
│   ├── repositories/
│   ├── stores/
│   ├── sync/
│   ├── clock/
│   └── id_generator/
├── infrastructure/
│   ├── local/
│   │   ├── memory/
│   │   └── sqlite/
│   ├── remote/
│   │   ├── memory/
│   │   └── http/
│   └── serializers/
├── sync/
│   ├── engine/
│   ├── conflicts/
│   └── reports/
└── shared/
    ├── typing/
    └── utils/

tests/
├── application/
├── domain/
├── infrastructure/
├── sync/
└── shared/

docs/
├── dev_diary.md
└── tests/
    └── coverage/
```
## 21. Exigences de test

### 21.1 Tests unitaires
À prévoir au minimum pour :
- entités ;
- validateurs ;
- services applicatifs ;
- règles métier ;
- exceptions ;
- moteur de synchronisation ;
- résolution de conflits ;
- implémentations mémoire.

### 21.2 Tests d’intégration
À prévoir pour :
- persistance locale ;
- cycle offline puis synchronisation ;
- détection de conflits ;
- cohérence des relations entre entités.

### 21.3 Tests de non-régression
À prévoir pour :
- déplacements de copies ;
- hiérarchie de contenants ;
- changements d’état de synchronisation ;
- fusion d’états locaux et distants.

## 22. Livrables attendus

### 22.1 Livrables code
- librairie Python installable ;
- code source complet ;
- implémentation mémoire minimale pour tests ;
- interfaces de persistance et sync ;
- services applicatifs ;
- exceptions personnalisées.

### 22.2 Livrables documentation
- `README.md`
- `CHANGELOG.md`
- `docs/dev_diary.md`
- documentation d’architecture ;
- documentation des cas d’usage ;
- exemples d’utilisation.

### 22.3 Livrables qualité
- configuration complète `pyproject.toml` ;
- suite de tests complète ;
- rapport de couverture ;
- conformité aux outils qualité.

## 23. Critères d’acceptation

Le projet sera considéré conforme si :

1. la librairie est installable et importable ;
2. les entités métier principales existent ;
3. les services applicatifs couvrent les cas d’usage de base ;
4. les validations métier sont en place ;
5. le fonctionnement offline-first est démontrable ;
6. le journal des changements existe ;
7. une synchronisation locale / distante abstraite fonctionne ;
8. la gestion minimale des conflits est présente ;
9. les exceptions spécifiques du projet sont implémentées ;
10. la couverture de tests atteint au moins 90 % ;
11. tous les outils qualité passent ;
12. la documentation de base est fournie.

## 24. Critères de réussite pour une première version stable

La version **`v1.0.0`** du présent dépôt est sortie avec les objectifs suivants **remplis au
niveau du noyau livré** (sans backend distant imposé — la synchro reste abstraite) :

- stabilité de l’API publique documentée (`__all__`, racine minimale) ;
- cohérence du modèle métier et des services applicatifs ;
- persistance via **ports** ; adaptateurs mémoire de référence ;
- synchronisation **local / distant** modélisée (DTO, plans, conflits) ;
- gestion documentée des conflits (détection, stratégies injectables) ;
- documentation README + `docs/` ;
- tests complets et reproductibles, couverture ≥ 90 % ;
- classifier *Production/Stable* et versioning SemVer à partir de **1.0.0**.

## 25. Découpage recommandé en grandes fonctionnalités

### 25.1 Bootstrap du projet
- structure du package ;
- `pyproject.toml` ;
- outils qualité ;
- configuration tests ;
- CI locale.

### 25.2 Noyau domaine
- entités ;
- value objects ;
- enums ;
- exceptions ;
- validateurs.

### 25.3 Repositories et ports
- interfaces de repositories ;
- interfaces de store ;
- génération d’identifiants ;
- horloge abstraite.

### 25.4 Services applicatifs
- usagers ;
- cartes ;
- copies ;
- contenants ;
- inventaire.

### 25.5 Implémentation locale mémoire
- repositories mémoire ;
- tests d’intégration de base.

### 25.6 Journal des changements
- création des change sets ;
- suivi des opérations ;
- statut de synchronisation.

### 25.7 Moteur de synchronisation
- push ;
- pull ;
- bidirectionnel ;
- rapports ;
- erreurs.

### 25.8 Gestion des conflits
- détection ;
- stratégies ;
- tests dédiés.

### 25.9 Implémentation locale persistante
- backend local concret ;
- sérialisation ;
- reprise de session.

### 25.10 Documentation et release
- README ;
- changelog ;
- diary ;
- préparation version.

## 26. Exemples d’usages attendus

### 26.1 Exemple métier simple
- créer un usager ;
- créer une carte logique ;
- créer deux copies physiques ;
- créer un contenant ;
- placer les copies dans le contenant ;
- calculer l’inventaire du contenant.

### 26.2 Exemple offline-first
- créer et déplacer des copies sans connexion ;
- consulter les changements en attente ;
- relancer l’application ;
- retrouver l’état local intact.

### 26.3 Exemple synchronisation
- pousser les changements vers le distant ;
- récupérer des changements distants ;
- détecter un conflit de version ;
- produire un rapport de synchronisation.

## 27. Points d’attention

- bien distinguer **carte logique** et **copie physique** ;
- bien distinguer **contenance hiérarchique** et **propriété** ;
- ne pas coupler le domaine à un stockage précis ;
- ne pas coupler la synchronisation à HTTP uniquement ;
- traiter les conflits comme une vraie responsabilité du cœur métier ;
- garantir la cohérence des liens entre entités.

## 28. Résumé exécutif

`baobab-collection-core` doit devenir une librairie Python de référence pour la gestion métier d’une collection de cartes physiques. Elle doit modéliser usagers, cartes, copies et contenants, offrir des services métier clairs, fonctionner hors ligne, journaliser les changements et synchroniser les états local et distant via des abstractions propres. Le tout doit respecter des standards élevés de qualité, de documentation, de typage, de tests et de maintenabilité.
