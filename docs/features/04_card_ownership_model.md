# Feature 04 — Card ownership model

## Objectif
Implémenter le modèle métier de la carte possédée, distinct de la copie physique.

## Finalité
Cette feature doit permettre de représenter une carte dans la collection comme référence métier, sur laquelle s’agrègeront les copies physiques.

## Périmètre
- entité carte ;
- attributs de référence et de classification ;
- repository port ;
- services ou cas d’usage ;
- validations métier ;
- tests.

## Hors périmètre
- copies physiques détaillées ;
- gestion de localisation physique ;
- synchronisation avancée ;
- import externe.

## Données minimales
- identifiant interne ;
- identifiant externe optionnel ;
- nom ;
- édition optionnelle ;
- version optionnelle ;
- langue optionnelle ;
- tags optionnels ;
- métadonnées ;
- état de synchronisation.

## Règles métier
- une carte représente une référence de collection, pas un exemplaire physique ;
- une carte doit pouvoir être retrouvée de manière fiable ;
- le modèle doit pouvoir accueillir des attributs métier sans coupler la librairie à une source de données externe.

## Cas d’usage attendus
- enregistrer une carte ;
- modifier les métadonnées éditables ;
- retrouver une carte ;
- lister les cartes ;
- empêcher les données incohérentes ;
- préparer l’agrégation future avec les copies physiques.

## Critères d’acceptation
- le modèle sépare clairement carte et copie ;
- les validations métier sont en place ;
- les cas d’usage de base fonctionnent ;
- l’ensemble est prêt pour la feature sur les copies physiques.