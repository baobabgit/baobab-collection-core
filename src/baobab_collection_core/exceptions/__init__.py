"""Exceptions spécifiques à *baobab-collection-core*."""

from .baobab_collection_core_exception import BaobabCollectionCoreException
from .duplicate_user_exception import DuplicateUserException
from .invalid_user_exception import InvalidUserException
from .user_not_found_exception import UserNotFoundException
from .validation_exception import ValidationException

__all__: list[str] = [
    "BaobabCollectionCoreException",
    "DuplicateUserException",
    "InvalidUserException",
    "UserNotFoundException",
    "ValidationException",
]
