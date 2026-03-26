# Publication v1.0.0 — GitHub Release et PyPI

Ce document prépare une **publication manuelle** propre. Il ne déclenche aucune action distante : à exécuter par un mainteneur disposant des droits GitHub et PyPI.

**Tag cible** : `v1.0.0` (préfixe `v` + SemVer du package **1.0.0**).

**Commit à taguer** : le dernier commit de `main` qui contient déjà `version = "1.0.0"` dans `pyproject.toml` et la section `[1.0.0]` dans `CHANGELOG.md` (vérifier avec `git log -1` et les fichiers ci-dessous).

---

## 1. Vérification de cohérence finale (avant tag)

| Élément | Attendu | Où vérifier |
|---------|---------|-------------|
| Version package | `1.0.0` | `pyproject.toml` → `[project].version` |
| Repli `__version__` | `1.0.0` | `src/baobab_collection_core/__init__.py` |
| Changelog | Section `## [1.0.0]` | `CHANGELOG.md` |
| README | Annonce stable **1.0.0** | `README.md` (entête + versioning) |
| Classifier PyPI | `Production/Stable` | `pyproject.toml` → `classifiers` |
| Typage distribué | `py.typed` empaqueté | `[tool.setuptools.package-data]` + présence dans le wheel |
| Artefacts | `baobab_collection_core-1.0.0-*.whl` et `.tar.gz` | Après `python -m build` (noms alignés sur la version) |

Commandes de contrôle rapide (depuis la racine du dépôt) :

```bash
git checkout main
git pull origin main
python -m pip install -e ".[dev]"
python -m pytest -q
python -m build --sdist --wheel
python -m pip install twine
python -m twine check dist/baobab_collection_core-1.0.0*
```

Corriger toute erreur de `twine check` avant upload.

---

## 2. Contenu proposé — release GitHub

### Titre (champ « Release title »)

```text
baobab-collection-core v1.0.0
```

### Description (coller dans le corps de la release, Markdown)

```markdown
## Première release stable

**baobab-collection-core 1.0.0** est la première version **stable** au sens [SemVer](https://semver.org/) : le domaine métier, les ports, l’application et les abstractions de synchronisation (offline-first, journal, détection / résolution de conflits) sont considérés comme **gelés** pour les symboles exportés via `__all__` dans les sous-packages documentés.

### Points clés

- **Domaine** : usagers, cartes, exemplaires physiques, contenants, métadonnées de version et de synchro, mutations locales.
- **Application** : services CRUD, inventaire (`CollectionBusinessService`), journal (`MutationTrackingService`), cœur de synchro et résolution de conflits.
- **Ports** : contrats de persistance et d’instantanés distants ; **infrastructure** : adaptateurs mémoire de référence.
- **Qualité** : typage strict (`py.typed`), tests (unitaires + intégration), couverture ≥ 90 %.

### Contrat d’API

- **Racine du package** : uniquement `BaobabCollectionCoreException` et `__version__`.
- **API stable** : imports depuis `domain`, `application`, `ports`, `infrastructure`, `exceptions` selon les listes `__all__` (voir README).

### Migration depuis les préversions 0.x

- Les releases **0.x** étaient des itérations de cadrage ; pour une base de code existante, **épinglez** la dépendance en SemVer (`~=1.0.0` ou `>=1.0.0,<2`) et adaptez les imports si vous pointiez encore vers des chemins non documentés.
- Détail des livraisons : [CHANGELOG.md](https://github.com/baobabgit/baobab-collection-core/blob/main/CHANGELOG.md).

### Artefacts

Joindre à la release GitHub les fichiers générés localement :

- `baobab_collection_core-1.0.0-py3-none-any.whl`
- `baobab_collection_core-1.0.0.tar.gz`

(répertoire `dist/` après `python -m build`, non versionné dans le dépôt).
```

---

## 3. Tag Git `v1.0.0`

Sur le commit **exact** qui sera publié (généralement `main` à jour) :

```bash
git fetch origin
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release 1.0.0 — première version stable"
git push origin v1.0.0
```

Vérifier sur GitHub que le tag pointe vers le bon commit avant de créer la release depuis ce tag (ou créer la release via l’UI en choisissant `v1.0.0`).

---

## 4. Build des artefacts

```bash
python -m pip install -U build
rm -rf dist build  # Unix ; sous PowerShell : Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
python -m build --sdist --wheel
```

Fichiers attendus dans `dist/` :

- `baobab_collection_core-1.0.0-py3-none-any.whl`
- `baobab_collection_core-1.0.0.tar.gz`

---

## 5. Publication PyPI (processus)

Prérequis : compte [PyPI](https://pypi.org/) et [API token](https://pypi.org/help/#apitoken) (ou identifiants dépréciés mais encore possibles). Ne jamais committer de secrets.

### Contrôle puis upload

```bash
python -m pip install -U twine
python -m twine check dist/baobab_collection_core-1.0.0*
```

**Index de production** :

```bash
python -m twine upload dist/baobab_collection_core-1.0.0*
```

*(Sans `--repository-url`, twine cible PyPI par défaut.)*

### TestPyPI (optionnel, brouillon)

```bash
python -m twine upload --repository testpypi dist/baobab_collection_core-1.0.0*
```

Puis `pip install -i https://test.pypi.org/simple/ baobab-collection-core==1.0.0` dans un venv propre pour valider.

### Après publication

- Vérifier la fiche projet : `https://pypi.org/project/baobab-collection-core/1.0.0/`
- `pip install baobab-collection-core==1.0.0` dans un environnement neuf.

---

## 6. Ordre recommandé (sans ambiguïté)

1. `main` à jour, QA locale (pytest, etc.).
2. `python -m build` + `twine check`.
3. Tag annoté `v1.0.0` + `git push origin v1.0.0`.
4. Créer la **GitHub Release** depuis le tag, coller le corps ci-dessus, joindre les deux fichiers `dist/`.
5. `twine upload` vers PyPI.
6. Smoke test `pip install` depuis PyPI.

---

## 7. Note sur cette livraison documentaire

Aucune publication réelle n’est effectuée par le dépôt lui-même : ce fichier sert de **procédure** et de **brouillon de release** pour les mainteneurs.
