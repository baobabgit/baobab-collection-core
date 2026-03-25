"""Point d’entrée minimal du package *baobab-collection-core* (release 1.x).

Seuls ``BaobabCollectionCoreException`` et ``__version__`` sont réexportés ici.
L’API stable complète habite les sous-packages ``domain``, ``application``,
``ports``, ``infrastructure`` et ``exceptions`` (voir ``__all__`` de chacun).
"""

from importlib.metadata import PackageNotFoundError, version

from baobab_collection_core.exceptions import BaobabCollectionCoreException

try:
    __version__: str = version("baobab-collection-core")
except PackageNotFoundError:
    __version__ = "1.0.0"

__all__: list[str] = [
    "BaobabCollectionCoreException",
    "__version__",
]
