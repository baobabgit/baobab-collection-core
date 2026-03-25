# Feature 06 — Container management

## Objectif
Implémenter la gestion des contenants physiques ou logiques de rangement.

## Finalité
Cette feature doit permettre d’organiser les copies physiques dans une arborescence de contenants, sans créer d’incohérences structurelles.

## Périmètre
- entité contenant ;
- hiérarchie parent/enfant ;
- validations de structure ;
- prévention des cycles ;
- repository port ;
- cas d’usage ;
- tests.

## Hors périmètre
- synchronisation avancée ;
- stratégie de résolution de conflits ;
- moteur de requêtes complexe.

## Données minimales
- identifiant ;
- nom ;
- type de contenant ;
- parent optionnel ;
- statut actif/archivé ;
- métadonnées ;
- version ;
- état de synchronisation.

## Types minimaux supportés
Le modèle doit être extensible pour :
- boîte ;
- classeur ;
- deck box ;
- pile ;
- zone temporaire ;
- regroupement logique.

## Règles métier
- un contenant ne peut pas être son propre parent ;
- un contenant ne peut pas créer de cycle ;
- un contenant archivé reste historisable ;
- la suppression physique d’un contenant non vide doit être empêchée ou strictement contrôlée.

## Cas d’usage attendus
- créer un contenant ;
- modifier un contenant ;
- archiver un contenant ;
- rattacher à un parent ;
- déplacer dans la hiérarchie ;
- parcourir l’arborescence ;
- lister les enfants directs.

## Critères d’acceptation
- la hiérarchie de contenants fonctionne ;
- les cycles sont empêchés ;
- le modèle est prêt à accueillir les copies physiques ;
- les cas d’usage clés sont testés.