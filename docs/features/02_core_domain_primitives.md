# Feature 02 — Core domain primitives

## Objectif
Mettre en place les primitives de domaine communes sur lesquelles reposera tout le cœur métier de la librairie.

## Finalité
Cette feature doit établir les briques fondamentales partagées entre les futures entités, value objects, états de synchronisation, métadonnées et mécanismes de versionnement.

## Périmètre
Cette feature couvre :

- les identifiants de domaine ;
- les métadonnées communes ;
- les états de synchronisation ;
- les versions d’entités ;
- les value objects de base ;
- les enums transverses ;
- les exceptions de validation de base.

## Hors périmètre
- les entités métier complètes ;
- les repositories ;
- la synchronisation détaillée ;
- les cas d’usage applicatifs.

## Livrables attendus
- base entity abstraite si pertinente ;
- value objects partagés ;
- identifiant générique ou spécialisable ;
- enums d’état de synchronisation ;
- métadonnées de création/modification ;
- base pour gestion de version ;
- exceptions de validation.

## Éléments attendus
### Identifiants
Prévoir un modèle d’identifiant stable, typé et sérialisable.

### Métadonnées
Prévoir au minimum :
- `created_at`
- `updated_at`
- éventuellement `deleted_at`
- version
- indicateurs de synchronisation

### Synchronisation
Prévoir un enum ou modèle équivalent pour les états :
- clean
- dirty
- synced
- conflict
- sync_error
- deleted

### Validation
Prévoir les validations minimales de cohérence des primitives.

## Exigences techniques
- classes immuables si pertinent pour les value objects ;
- typage complet ;
- comparaison explicite ;
- sérialisation simple possible ;
- pas de dépendance à un stockage concret.

## Exigences qualité
- tests unitaires exhaustifs ;
- cas nominaux et cas d’erreur ;
- documentation des primitives publiques.

## Critères d’acceptation
- les primitives sont réutilisables par les futures features ;
- les états de synchronisation sont centralisés ;
- les validations de base sont testées ;
- les abstractions sont suffisamment simples et extensibles.