# Feature 10 — Conflict detection and resolution

## Objectif
Implémenter la détection et la résolution des conflits de synchronisation.

## Finalité
Cette feature doit permettre d’identifier les divergences entre états local et distant et d’appliquer une stratégie explicite de résolution.

## Périmètre
- modèle de conflit ;
- détection de conflit ;
- stratégies de résolution ;
- résolution explicite ;
- tests.

## Hors périmètre
- interface utilisateur de résolution manuelle ;
- synchronisation réseau concrète.

## Types de conflits à prévoir
- modification concurrente locale/distante ;
- suppression distante d’une entité modifiée localement ;
- divergence de version ;
- changement concurrent de parent/contenant ;
- collision d’identifiants externes.

## Stratégies minimales
Le design doit permettre :
- local prioritaire ;
- distant prioritaire ;
- conflit explicite à remonter ;
- base extensible pour fusion future.

## Critères d’acceptation
- les conflits sont détectés ;
- les stratégies sont injectables ;
- les principaux scénarios sont testés.