"""Exceptions spécifiques à *baobab-collection-core*."""

from .baobab_collection_core_exception import BaobabCollectionCoreException
from .card_not_found_exception import CardNotFoundException
from .duplicate_card_exception import DuplicateCardException
from .duplicate_user_exception import DuplicateUserException
from .invalid_card_exception import InvalidCardException
from .invalid_physical_copy_exception import InvalidPhysicalCopyException
from .invalid_user_exception import InvalidUserException
from .physical_copy_not_found_exception import PhysicalCopyNotFoundException
from .user_not_found_exception import UserNotFoundException
from .validation_exception import ValidationException

__all__: list[str] = [
    "BaobabCollectionCoreException",
    "CardNotFoundException",
    "DuplicateCardException",
    "DuplicateUserException",
    "InvalidCardException",
    "InvalidPhysicalCopyException",
    "InvalidUserException",
    "PhysicalCopyNotFoundException",
    "UserNotFoundException",
    "ValidationException",
]
