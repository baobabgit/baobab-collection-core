"""Ports : interfaces (abstractions) vers l'extérieur (persistance, horloge, etc.)."""

from baobab_collection_core.ports.card_repository_port import CardRepositoryPort
from baobab_collection_core.ports.container_repository_port import ContainerRepositoryPort
from baobab_collection_core.ports.local_mutation_journal_port import LocalMutationJournalPort
from baobab_collection_core.ports.physical_copy_repository_port import PhysicalCopyRepositoryPort
from baobab_collection_core.ports.remote_entity_sync_snapshot_port import (
    RemoteEntitySyncSnapshotPort,
)
from baobab_collection_core.ports.user_repository_port import UserRepositoryPort

__all__: list[str] = [
    "CardRepositoryPort",
    "ContainerRepositoryPort",
    "LocalMutationJournalPort",
    "PhysicalCopyRepositoryPort",
    "RemoteEntitySyncSnapshotPort",
    "UserRepositoryPort",
]
