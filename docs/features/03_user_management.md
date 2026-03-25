# Feature 03 — User management

## Objectif
Implémenter la gestion des usagers de la collection.

## Finalité
Cette feature doit fournir le modèle métier, les règles de validation et les cas d’usage de base permettant de créer, mettre à jour, désactiver, retrouver et lister des usagers.

## Périmètre
- entité usager ;
- validations métier ;
- repository port ;
- services ou cas d’usage applicatifs ;
- exceptions spécifiques ;
- tests unitaires.

## Hors périmètre
- authentification ;
- gestion des droits ;
- synchronisation avancée des usagers ;
- interface utilisateur.

## Données minimales
Un usager doit inclure au minimum :
- identifiant ;
- nom affiché ;
- statut actif/inactif ;
- métadonnées ;
- version ;
- état de synchronisation.

## Règles métier
- un usager doit avoir un nom valide ;
- un usager désactivé reste historisé ;
- la suppression physique n’est pas le comportement par défaut ;
- les modifications doivent mettre à jour la version et l’état de synchronisation.

## Cas d’usage attendus
- créer un usager ;
- modifier un usager ;
- désactiver un usager ;
- récupérer un usager par identifiant ;
- lister les usagers ;
- refuser les données invalides.

## Exigences techniques
- port de repository dédié ;
- cas d’usage ou service applicatif clair ;
- pas de dépendance à un stockage concret ;
- exceptions métier explicites.

## Exigences qualité
- tests des validations ;
- tests des cas d’usage ;
- tests des erreurs ;
- documentation publique.

## Critères d’acceptation
- un usager peut être créé, modifié et désactivé ;
- les règles de validation sont appliquées ;
- les erreurs sont portées par des exceptions spécifiques ;
- le design est réutilisable par les futures features.