"""Faux fournisseur d'instantanés distants pour les tests de synchro."""

from __future__ import annotations

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.sync_dtos import RemoteEntitySyncSnapshot
from baobab_collection_core.ports.remote_entity_sync_snapshot_port import (
    RemoteEntitySyncSnapshotPort,
)


class FakeRemoteEntitySyncSnapshotProvider(RemoteEntitySyncSnapshotPort):
    """Stockage en mémoire keyed par (entity_id, kind)."""

    __slots__ = ("_data",)

    def __init__(self) -> None:
        self._data: dict[tuple[str, str], RemoteEntitySyncSnapshot] = {}

    def seed(self, snapshot: RemoteEntitySyncSnapshot, kind: LocalEntityKind) -> None:
        """Enregistre l'instantané pour une clé."""
        self._data[(snapshot.entity_id.value, kind.value)] = snapshot

    def fetch_snapshot(
        self, entity_id: DomainId, entity_kind: LocalEntityKind
    ) -> RemoteEntitySyncSnapshot:
        """Voir :meth:`RemoteEntitySyncSnapshotPort.fetch_snapshot`."""
        key = (entity_id.value, entity_kind.value)
        if key not in self._data:
            return RemoteEntitySyncSnapshot(
                entity_id=entity_id,
                present=False,
                version=0,
                is_logically_deleted=False,
            )
        return self._data[key]
