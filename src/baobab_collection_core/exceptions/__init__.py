"""Exceptions spécifiques à *baobab-collection-core*."""

from .baobab_collection_core_exception import BaobabCollectionCoreException
from .validation_exception import ValidationException

__all__: list[str] = [
    "BaobabCollectionCoreException",
    "ValidationException",
]
