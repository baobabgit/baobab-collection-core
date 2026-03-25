# Feature 08 — Offline-first local mutation tracking

## Objectif
Mettre en place le mécanisme local de suivi des modifications dans une logique offline-first.

## Finalité
Cette feature doit permettre d’exécuter les opérations métier localement, de marquer les entités modifiées et de conserver un journal exploitable pour une synchronisation ultérieure.

## Périmètre
- état dirty/local ;
- journal des mutations ;
- événements de mutation ;
- extraction des changements en attente ;
- marquage de synchronisation ;
- tests.

## Hors périmètre
- synchronisation réseau effective ;
- transport distant ;
- résolution complète des conflits.

## Capacités attendues
- marquer une entité comme modifiée localement ;
- créer un enregistrement de mutation ;
- lister les changements en attente ;
- rejouer ou exposer les mutations si nécessaire ;
- distinguer les états propres, modifiés, synchronisés, en conflit ou en erreur.

## Règles métier
- toute modification locale significative doit être traçable ;
- le journal doit être suffisamment riche pour permettre une synchronisation ultérieure ;
- la suppression logique doit être représentée comme une mutation.

## Critères d’acceptation
- une mutation locale est traçable ;
- les changements en attente sont récupérables ;
- les états de synchronisation sont mis à jour de façon cohérente ;
- les cas principaux sont testés.