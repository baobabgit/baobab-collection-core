"""Modèle de conflit matérialisé après détection."""

from __future__ import annotations

from dataclasses import dataclass

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.sync_conflict_kind import SyncConflictKind


@dataclass(frozen=True, slots=True)
class SyncConflict:
    """Instance de conflit décorrélée du transport (pas d'HTTP ni de persistance).

    :ivar entity_id: Entité concernée.
    :ivar entity_kind: Famille métier.
    :ivar kind: Sous-type de conflit.
    :ivar summary: Message stable pour journaux ou UI future.
    :ivar local_version: Version observée localement au moment de la détection.
    :ivar remote_version: Version distante si connue, sinon ``None``.
    """

    entity_id: DomainId
    entity_kind: LocalEntityKind
    kind: SyncConflictKind
    summary: str
    local_version: int
    remote_version: int | None
