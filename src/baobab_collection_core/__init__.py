"""API publique du package *baobab-collection-core*.

Ce package est le noyau pour la gestion de collections (cartes, exemplaires,
conteneurs, synchronisation offline-first, etc.).
"""

from importlib.metadata import PackageNotFoundError, version

from baobab_collection_core.exceptions import BaobabCollectionCoreException

try:
    __version__: str = version("baobab-collection-core")
except PackageNotFoundError:
    __version__ = "0.7.0"

__all__: list[str] = [
    "BaobabCollectionCoreException",
    "__version__",
]
