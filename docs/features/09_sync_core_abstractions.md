# Feature 09 — Sync core abstractions

## Objectif
Implémenter les abstractions centrales de synchronisation entre état local et état distant.

## Finalité
Cette feature doit fournir les ports, modèles et services nécessaires pour comparer, préparer et appliquer une synchronisation sans imposer un backend particulier.

## Périmètre
- ports de synchronisation ;
- DTO ou modèles de comparaison ;
- plan de synchronisation ;
- application de résultats ;
- mise à jour des états de sync ;
- tests.

## Hors périmètre
- client HTTP concret ;
- backend concret ;
- résolution avancée des conflits.

## Capacités attendues
- comparer local et distant ;
- identifier à créer, mettre à jour, supprimer ou fusionner ;
- produire un plan de synchronisation ;
- appliquer un résultat de synchronisation ;
- marquer les entités comme synchronisées ou en erreur.

## Critères d’acceptation
- les abstractions de sync existent et sont testables ;
- le cœur ne dépend d’aucun backend ;
- la future intégration d’un adaptateur distant est rendue possible.