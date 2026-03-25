# Feature 07 — Collection business services

## Objectif
Implémenter les services métier de collection permettant d’agréger, compter, localiser et exposer les indicateurs métier principaux.

## Finalité
Cette feature doit fournir la logique métier transverse qui exploite les cartes, copies et contenants pour produire une vision exploitable de la collection.

## Périmètre
- services métier d’inventaire ;
- agrégations ;
- statistiques simples ;
- localisation ;
- disponibilité ;
- détection de doublons simples ;
- tests.

## Hors périmètre
- synchronisation détaillée ;
- résolution de conflits ;
- reporting avancé ;
- moteur de recherche full-text.

## Capacités attendues
- compter les cartes distinctes ;
- compter les copies totales ;
- compter les copies disponibles ;
- localiser une copie ;
- localiser toutes les copies d’une carte ;
- lister le contenu d’un contenant ;
- détecter des doublons logiques simples ;
- produire des agrégats orientés interface.

## Règles métier
- les agrégats doivent être cohérents avec les données sources ;
- les cartes distinctes ne doivent pas être confondues avec le nombre total de copies ;
- les copies supprimées logiquement ou indisponibles doivent être traitées selon des règles explicites.

## Critères d’acceptation
- les principaux indicateurs métier sont disponibles ;
- les services sont testés ;
- les règles de comptage sont explicites et documentées.