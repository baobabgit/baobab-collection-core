# Exécution checklist de release — v1.0.0

Date de la passe : **2026-03-25**. Branche : `feature/run-release-checklist-1-0-0`.  
Python **3.13.12**, venv projet `.venv`, racine du dépôt.

Référence : [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

Légende : **Conforme** = vérification exécutée avec succès ou preuve lue dans le dépôt.

---

## Code et API

| # | Critère | Statut | Preuve |
|---|---------|--------|--------|
| 1 | `pyproject.toml` : version SemVer = CHANGELOG | **Conforme** | `version = "1.0.0"` ; entrée `## [1.0.0]` dans [CHANGELOG.md](../CHANGELOG.md). |
| 2 | Classifier `Development Status :: 5 - Production/Stable` | **Conforme** | Ligne présente dans `[project].classifiers` du `pyproject.toml`. |
| 3 | Repli `__version__` si package non installé | **Conforme** | `__init__.py` : `except PackageNotFoundError: __version__ = "1.0.0"`. |
| 4 | `test_package.py` : repli `1.0.0` | **Conforme** | `test_version_fallback_when_metadata_missing` assert `"1.0.0"`. |
| 5 | Racine : symboles documentés uniquement | **Conforme** | `__all__` = `BaobabCollectionCoreException`, `__version__` ; test `test_public_api_contract.py`. |
| 6 | Pas de régression API README sans CHANGELOG | **Conforme** | README annonce v1.0.0 stable + contrat racine ; CHANGELOG 1.0.0 couvre packaging/doc (revue manuelle). |

---

## Qualité

| # | Critère | Statut | Preuve |
|---|---------|--------|--------|
| 7 | `pytest` + couverture ≥ seuil | **Conforme** | `pytest` : **197 passed** ; total **95,97 %** ; `fail_under = 90` respecté. |
| 8 | `black` — aucun reformattage | **Conforme** | `python -m black --check src tests` : *120 files would be left unchanged*. |
| 9 | `mypy src tests` | **Conforme** | *Success: no issues found in 120 source files*. |
| 10 | `pylint` | **Conforme** | `python -m pylint -j 0 --recursive=y src tests` : **10.00/10** (équivalent à couvrir `src` et `tests`). |
| 11 | `flake8 src tests` | **Conforme** | Sortie vide (succès). |
| 12 | `bandit -c pyproject.toml -r src` | **Conforme** | Sortie vide (succès). |

---

## Documentation

| # | Critère | Statut | Preuve |
|---|---------|--------|--------|
| 13 | README à jour | **Conforme** | Sections installation, concepts, liens `docs/` ; mention **1.0.0** et classifier ; extra `dev` inclut `build` (aligné `pyproject.toml`). |
| 14 | CHANGELOG section version + date + catégories | **Conforme** | `[1.0.0] - 2026-03-26` avec Résumé, Changed, Fixed, etc. |
| 15 | Guides architecture / domaine / synchro | **Conforme** | Fichiers présents et cohérents avec la structure packages (pas de contradiction « pré-release » détectée ; revue ciblée). |
| 16 | `features/README.md` index | **Conforme** | Les 12 fiches `01`–`12` existent ; la fiche **11** a été complétée lors de cette passe (était vide). |

---

## Distribution (manuelle)

| # | Critère | Statut | Preuve |
|---|---------|--------|--------|
| 17 | `python -m build` → sdist + wheel | **Conforme** | *Successfully built* `baobab_collection_core-1.0.0.tar.gz` et `...-py3-none-any.whl`. |
| 18 | `pip install` wheel dans venv propre | **Conforme** | Venv local `.rc-checklist-venv/` (gitignore) ; `pip install dist/...whl` OK. |
| 19 | Import package + chemins documentés | **Conforme** | `import baobab_collection_core` ; `__version__ == "1.0.0"` ; `from baobab_collection_core.domain import DomainId` OK. |

---

## Communication

| # | Critère | Statut | Preuve |
|---|---------|--------|--------|
| 20 | `dev_diary.md` | **Conforme** | Entrée **2026-03-25 (checklist release v1.0.0)** ajoutée. |
| 21 | PR / notes consommateurs | **Conforme** | PR GitHub associée au merge de cette branche (notes dans la description de PR). |

---

## Post-release (optionnel)

| # | Critère | Statut | Commentaire |
|---|---------|--------|-------------|
| 22 | Tag `v1.0.0` | **Non exécuté** | Hors périmètre automatisé ; à faire manuellement sur le commit de release. |
| 23 | Publication PyPI | **Non exécuté** | Politique Baobab / manuel ; checklist ne publie pas. |

---

## Synthèse

- **Checklist opérationnelle (pré-tag / pré-publication)** : **soldée** pour la v1.0.0 — tous les items obligatoires **Conformes** ; optionnels **non faits** (tag, PyPI), documentés.
- **Points résiduels** : créer le tag Git et publier sur l’index de paquets selon votre processus interne.
