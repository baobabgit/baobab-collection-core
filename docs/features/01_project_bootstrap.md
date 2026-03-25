# Feature 01 — Project bootstrap

## Objectif
Mettre en place les fondations techniques, structurelles et qualitatives de la librairie `baobab-collection-core` afin de permettre un développement propre, modulaire, testable et industrialisable.

## Finalité
Cette feature doit produire un dépôt Python immédiatement exploitable pour les développements suivants, avec une structure claire, un packaging moderne, une configuration centralisée et les outils qualité du projet.

## Périmètre
Cette feature couvre :

- l’initialisation de la structure du projet ;
- la création du package Python principal ;
- la configuration de `pyproject.toml` ;
- la mise en place des outils qualité ;
- l’ajout des fichiers standards du dépôt ;
- la préparation des répertoires source, tests et documentation ;
- la création de l’exception racine du projet ;
- la préparation du journal de développement.

## Hors périmètre
Cette feature ne couvre pas encore :

- les entités métier détaillées ;
- la logique de collection ;
- la synchronisation ;
- les adaptateurs métiers concrets.

## Livrables attendus
- structure `src/` complète ;
- package `baobab_collection_core` importable ;
- `pyproject.toml` complet ;
- configuration outillage : black, pylint, flake8, mypy, pytest, coverage, bandit ;
- `README.md` initial ;
- `CHANGELOG.md` initial ;
- `docs/dev_diary.md` initial ;
- répertoire `tests/` structuré ;
- exception racine projet ;
- fichier `py.typed`.

## Arborescence minimale attendue
```text
src/baobab_collection_core/
tests/
docs/
docs/features/

## Exigences fonctionnelles
- le package doit être importable après installation editable ;
- la commande de tests doit fonctionner ;
- la couverture doit être activable ;
- les outils qualité doivent être configurés ;
- le projet doit être prêt à accueillir les futures classes, une classe par fichier.
- Exigences techniques
- Python >= 3.11 ;
- code sous src/ ;
- typage activé ;
- longueur de ligne 100 ;
- configuration centralisée dans pyproject.toml autant que possible.
- Exigences qualité
- tests unitaires initiaux ;
- import package validé ;
- aucune erreur bloquante de lint sur le socle ;
- conventions de nommage cohérentes ;
- docstrings sur les éléments publics.

## Critères d’acceptation
- pip install -e . fonctionne ;
- import baobab_collection_core fonctionne ;
- pytest fonctionne ;
- les outils qualité sont configurés ;
- le dépôt contient les fichiers standards de base ;
- l’exception racine du projet existe.

## Dépendances
Aucune.

## Risques
- sur-configuration prématurée ;
- structure trop rigide ;
- oubli d’un élément de packaging.
- Notes d’implémentation

Préparer une structure extensible orientée domaine, sans introduire encore de logique métier inutile.