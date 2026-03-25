"""Accès abstrait à l'instantané distant d'une entité (sans protocole réseau)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from baobab_collection_core.domain.sync_dtos import RemoteEntitySyncSnapshot
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind


class RemoteEntitySyncSnapshotPort(ABC):
    """Fournisseur d'état pair pour comparaison ; implémenté par adaptateurs futurs."""

    @abstractmethod
    def fetch_snapshot(
        self, entity_id: DomainId, entity_kind: LocalEntityKind
    ) -> RemoteEntitySyncSnapshot:
        """Retourne toujours un DTO : ``present=False`` si l'entité n'existe pas distamment."""
