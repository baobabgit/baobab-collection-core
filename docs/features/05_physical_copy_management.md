# Feature 05 — Physical copy management

## Objectif
Implémenter la gestion des copies physiques de cartes.

## Finalité
Cette feature doit représenter chaque exemplaire physique concret possédé, avec son état propre, son rattachement à une carte, à un usager et potentiellement à un contenant.

## Périmètre
- entité copie physique ;
- états et statuts ;
- rattachement à la carte ;
- rattachement au propriétaire/usager ;
- rattachement optionnel à un contenant ;
- validations ;
- repository port ;
- cas d’usage ;
- tests.

## Hors périmètre
- logique avancée de navigation des contenants ;
- synchronisation détaillée ;
- résolution de conflits.

## Données minimales
- identifiant ;
- identifiant de carte ;
- identifiant d’usager/propriétaire ;
- contenant courant optionnel ;
- emplacement optionnel ;
- état physique ;
- statut métier ;
- langue optionnelle ;
- finition optionnelle ;
- notes optionnelles ;
- métadonnées ;
- version ;
- état de synchronisation ;
- suppression logique.

## Règles métier
- une copie appartient à une seule carte ;
- une copie ne peut avoir qu’un état courant ;
- une copie ne peut avoir qu’un contenant courant à la fois ;
- les modifications doivent être historisables au moins techniquement ;
- la suppression logique doit être préférée à la suppression physique si l’objet participe à la synchronisation.

## Cas d’usage attendus
- créer une copie ;
- modifier une copie ;
- changer son état ;
- changer son statut ;
- rattacher/détacher un contenant ;
- supprimer logiquement une copie ;
- retrouver une copie ;
- lister les copies d’une carte.

## Critères d’acceptation
- le concept de copie physique est distinct de la carte ;
- les statuts et états sont centralisés ;
- les cas d’usage principaux sont testés ;
- les validations empêchent les incohérences.