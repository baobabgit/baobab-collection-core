"""Orchestration mince : détection puis résolution via stratégie injectée."""

from __future__ import annotations

from baobab_collection_core.application.sync_conflict_detector import SyncConflictDetector
from baobab_collection_core.application.sync_conflict_resolution_strategy import (
    SyncConflictResolutionStrategy,
)
from baobab_collection_core.domain.conflict_resolution_decision import ConflictResolutionDecision
from baobab_collection_core.domain.sync_conflict import SyncConflict
from baobab_collection_core.domain.sync_dtos import (
    LocalEntitySyncSnapshot,
    RemoteEntitySyncSnapshot,
)


class SyncConflictResolutionService:
    """Assemble détecteur et politique ; toute persistance reste hors de ce module."""

    __slots__ = ("_detector",)

    def __init__(self, detector: SyncConflictDetector | None = None) -> None:
        self._detector = detector if detector is not None else SyncConflictDetector()

    def detect_only(
        self,
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> SyncConflict | None:
        """Expose uniquement la détection (tests, diagnostics)."""
        return self._detector.detect(local, remote)

    @staticmethod
    def resolve_with_strategy(
        conflict: SyncConflict,
        *,
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
        strategy: SyncConflictResolutionStrategy,
    ) -> ConflictResolutionDecision:
        """Applique une stratégie sans passer par le détecteur."""
        return strategy.resolve(conflict, local=local, remote=remote)

    def detect_and_resolve(
        self,
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
        strategy: SyncConflictResolutionStrategy,
    ) -> tuple[SyncConflict | None, ConflictResolutionDecision | None]:
        """Enchaîne détection et résolution si un conflit est trouvé."""
        conflict = self.detect_only(local, remote)
        if conflict is None:
            return None, None
        decision = strategy.resolve(conflict, local=local, remote=remote)
        return conflict, decision
