"""Exceptions spécifiques à *baobab-collection-core*."""

from .baobab_collection_core_exception import BaobabCollectionCoreException
from .card_not_found_exception import CardNotFoundException
from .container_cycle_exception import ContainerCycleException
from .container_not_found_exception import ContainerNotFoundException
from .duplicate_card_exception import DuplicateCardException
from .duplicate_user_exception import DuplicateUserException
from .invalid_card_exception import InvalidCardException
from .invalid_container_exception import InvalidContainerException
from .invalid_local_mutation_exception import InvalidLocalMutationException
from .invalid_physical_copy_exception import InvalidPhysicalCopyException
from .invalid_sync_conflict_resolution_exception import InvalidSyncConflictResolutionException
from .invalid_sync_snapshot_exception import InvalidSyncSnapshotException
from .invalid_user_exception import InvalidUserException
from .mutation_not_found_exception import MutationNotFoundException
from .physical_copy_not_found_exception import PhysicalCopyNotFoundException
from .user_not_found_exception import UserNotFoundException
from .validation_exception import ValidationException

__all__: list[str] = [
    "BaobabCollectionCoreException",
    "CardNotFoundException",
    "ContainerCycleException",
    "ContainerNotFoundException",
    "DuplicateCardException",
    "DuplicateUserException",
    "InvalidCardException",
    "InvalidContainerException",
    "InvalidLocalMutationException",
    "InvalidPhysicalCopyException",
    "InvalidSyncConflictResolutionException",
    "InvalidSyncSnapshotException",
    "InvalidUserException",
    "MutationNotFoundException",
    "PhysicalCopyNotFoundException",
    "UserNotFoundException",
    "ValidationException",
]
