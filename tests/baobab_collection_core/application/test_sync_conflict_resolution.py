"""Tests de détection et résolution de conflits (sans transport)."""

import pytest

from baobab_collection_core.application.sync_conflict_detector import SyncConflictDetector
from baobab_collection_core.application.sync_conflict_resolution_service import (
    SyncConflictResolutionService,
)
from baobab_collection_core.application.sync_conflict_resolution_strategy import (
    ExplicitManualSyncConflictStrategy,
    LocalWinsSyncConflictStrategy,
    RemoteWinsSyncConflictStrategy,
)
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.sync_conflict import SyncConflict
from baobab_collection_core.domain.sync_conflict_kind import SyncConflictKind
from baobab_collection_core.domain.sync_dtos import (
    LocalEntitySyncSnapshot,
    RemoteEntitySyncSnapshot,
)
from baobab_collection_core.domain.sync_session_outcome import SyncSessionOutcome
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.invalid_sync_conflict_resolution_exception import (
    InvalidSyncConflictResolutionException,
)
from baobab_collection_core.exceptions.invalid_sync_snapshot_exception import (
    InvalidSyncSnapshotException,
)


class TestSyncConflictDetection:
    """Scénarios de détection par type."""

    @staticmethod
    def _eid(suffix: str = "01") -> DomainId:
        return DomainId(f"60000000-0000-4000-8000-0000000000{suffix}")

    @staticmethod
    def _pid(suffix: str = "aa") -> DomainId:
        return DomainId(f"70000000-0000-4000-8000-0000000000{suffix}")

    def test_detect_logical_external_id_collision(self) -> None:
        """Deux clés métier externes différentes pour la même entité."""
        det = SyncConflictDetector()
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=2,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
            external_business_key="SKU-A",
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid(),
            present=True,
            version=2,
            is_logically_deleted=False,
            external_business_key="SKU-B",
        )
        c = det.detect(local, remote)
        assert c is not None
        assert c.kind is SyncConflictKind.LOGICAL_EXTERNAL_ID_COLLISION

    def test_detect_remote_deleted_local_modified(self) -> None:
        """Tombeau serveur alors que le client a des changements locaux."""
        det = SyncConflictDetector()
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid("02"),
            entity_kind=LocalEntityKind.CONTAINER,
            version=3,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid("02"),
            present=True,
            version=3,
            is_logically_deleted=True,
        )
        c = det.detect(local, remote)
        assert c is not None
        assert c.kind is SyncConflictKind.REMOTE_DELETED_LOCAL_MODIFIED

    def test_detect_version_divergence(self) -> None:
        """Versions différentes avec travail local en attente."""
        det = SyncConflictDetector()
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid("03"),
            entity_kind=LocalEntityKind.COLLECTION_CARD,
            version=1,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid("03"),
            present=True,
            version=4,
            is_logically_deleted=False,
        )
        c = det.detect(local, remote)
        assert c is not None
        assert c.kind is SyncConflictKind.VERSION_DIVERGENCE

    def test_detect_concurrent_parent_change(self) -> None:
        """Contenants parents différents avec client dirty."""
        det = SyncConflictDetector()
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid("04"),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=5,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
            parent_container_id=self._pid("01"),
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid("04"),
            present=True,
            version=5,
            is_logically_deleted=False,
            parent_container_id=self._pid("02"),
        )
        c = det.detect(local, remote)
        assert c is not None
        assert c.kind is SyncConflictKind.CONCURRENT_PARENT_CHANGE

    def test_detect_concurrent_modification_same_revision(self) -> None:
        """Même révision mais empreintes de contenu divergentes."""
        det = SyncConflictDetector()
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid("05"),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=2,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
            content_fingerprint="fp-local",
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid("05"),
            present=True,
            version=2,
            is_logically_deleted=False,
            content_fingerprint="fp-remote",
        )
        c = det.detect(local, remote)
        assert c is not None
        assert c.kind is SyncConflictKind.CONCURRENT_MODIFICATION

    def test_detect_none_when_no_conflict_signals(self) -> None:
        """Pas de divergence selon les règles du détecteur."""
        det = SyncConflictDetector()
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid("06"),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=2,
            sync_state=SyncState.SYNCED,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid("06"),
            present=True,
            version=2,
            is_logically_deleted=False,
        )
        assert det.detect(local, remote) is None

    def test_mismatched_entity_id_raises(self) -> None:
        """Garde-fou sur la paire d'instantanés."""
        det = SyncConflictDetector()
        a = LocalEntitySyncSnapshot(
            entity_id=self._eid("07"),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=1,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        b = RemoteEntitySyncSnapshot(
            entity_id=self._eid("08"),
            present=True,
            version=1,
            is_logically_deleted=False,
        )
        with pytest.raises(InvalidSyncSnapshotException):
            det.detect(a, b)


class TestSyncConflictStrategies:
    """Politiques injectables."""

    @staticmethod
    def _eid() -> DomainId:
        return DomainId("61000000-0000-4000-8000-000000000001")

    def test_local_wins_marks_synced_with_local_version(self) -> None:
        """La branche locale devient la vérité adoptée."""
        conflict = SyncConflict(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            kind=SyncConflictKind.VERSION_DIVERGENCE,
            summary="x",
            local_version=2,
            remote_version=5,
        )
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=2,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
            parent_container_id=DomainId("62000000-0000-4000-8000-000000000099"),
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid(),
            present=True,
            version=5,
            is_logically_deleted=False,
        )
        decision = LocalWinsSyncConflictStrategy().resolve(conflict, local=local, remote=remote)
        assert decision.outcome is SyncSessionOutcome.SYNCED
        assert decision.winner == "local"
        assert decision.adopted_version == 2
        assert decision.adopted_parent_container_id == local.parent_container_id
        assert decision.requires_manual_resolution is False

    def test_remote_wins_marks_synced_with_remote_version(self) -> None:
        """On adopte la révision et le parent distants."""
        conflict = SyncConflict(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            kind=SyncConflictKind.CONCURRENT_PARENT_CHANGE,
            summary="y",
            local_version=5,
            remote_version=5,
        )
        pid = DomainId("63000000-0000-4000-8000-0000000000ab")
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=5,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid(),
            present=True,
            version=5,
            is_logically_deleted=False,
            parent_container_id=pid,
        )
        decision = RemoteWinsSyncConflictStrategy().resolve(conflict, local=local, remote=remote)
        assert decision.outcome is SyncSessionOutcome.SYNCED
        assert decision.winner == "remote"
        assert decision.adopted_version == 5
        assert decision.adopted_parent_container_id == pid

    def test_remote_wins_clears_parent_on_tombstone(self) -> None:
        """Si le distant est une tombe, aucun parent n'est conservé."""
        conflict = SyncConflict(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.CONTAINER,
            kind=SyncConflictKind.REMOTE_DELETED_LOCAL_MODIFIED,
            summary="z",
            local_version=1,
            remote_version=1,
        )
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.CONTAINER,
            version=1,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid(),
            present=True,
            version=1,
            is_logically_deleted=True,
            parent_container_id=DomainId("64000000-0000-4000-8000-000000000099"),
        )
        decision = RemoteWinsSyncConflictStrategy().resolve(conflict, local=local, remote=remote)
        assert decision.adopted_parent_container_id is None

    def test_explicit_strategy_surfaces_conflict(self) -> None:
        """Le conflit reste explicite pour une résolution manuelle ultérieure."""
        conflict = SyncConflict(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            kind=SyncConflictKind.CONCURRENT_MODIFICATION,
            summary="m",
            local_version=2,
            remote_version=2,
        )
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=2,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid(),
            present=True,
            version=2,
            is_logically_deleted=False,
        )
        decision = ExplicitManualSyncConflictStrategy().resolve(
            conflict, local=local, remote=remote
        )
        assert decision.outcome is SyncSessionOutcome.CONFLICT
        assert decision.winner == "manual"
        assert decision.requires_manual_resolution is True

    def test_remote_wins_without_remote_raises(self) -> None:
        """Impossible d'aligner sur le distant s'il est absent."""
        conflict = SyncConflict(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.COLLECTION_CARD,
            kind=SyncConflictKind.VERSION_DIVERGENCE,
            summary="n/a",
            local_version=1,
            remote_version=None,
        )
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.COLLECTION_CARD,
            version=1,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid(),
            present=False,
            version=0,
            is_logically_deleted=False,
        )
        with pytest.raises(InvalidSyncConflictResolutionException):
            RemoteWinsSyncConflictStrategy().resolve(conflict, local=local, remote=remote)


class TestSyncConflictResolutionService:
    """Chaîne détection + résolution."""

    @staticmethod
    def _eid() -> DomainId:
        return DomainId("65000000-0000-4000-8000-000000000001")

    def test_detect_and_resolve_local_wins(self) -> None:
        """Flux complet jusqu'à une décision SYNCED locale."""
        svc = SyncConflictResolutionService()
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=1,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid(),
            present=True,
            version=4,
            is_logically_deleted=False,
        )
        conflict, decision = svc.detect_and_resolve(local, remote, LocalWinsSyncConflictStrategy())
        assert conflict is not None
        assert decision is not None
        assert conflict.kind is SyncConflictKind.VERSION_DIVERGENCE
        assert decision.outcome is SyncSessionOutcome.SYNCED
        assert decision.winner == "local"

    def test_detect_only_and_resolve_with_strategy(self) -> None:
        """API utilitaires du service (hors détect_and_resolve)."""
        svc = SyncConflictResolutionService()
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=2,
            sync_state=SyncState.SYNCED,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid(),
            present=True,
            version=2,
            is_logically_deleted=False,
        )
        assert svc.detect_only(local, remote) is None

        conflict = SyncConflict(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            kind=SyncConflictKind.VERSION_DIVERGENCE,
            summary="",
            local_version=1,
            remote_version=4,
        )
        local_dirty = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=1,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        decision = svc.resolve_with_strategy(
            conflict,
            local=local_dirty,
            remote=remote,
            strategy=RemoteWinsSyncConflictStrategy(),
        )
        assert decision.winner == "remote"
        assert decision.adopted_version == 2

    def test_detect_and_resolve_without_conflict_returns_pair_of_none(self) -> None:
        """Si le détecteur ne voit rien, aucune décision n'est produite."""
        svc = SyncConflictResolutionService()
        local = LocalEntitySyncSnapshot(
            entity_id=self._eid(),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=1,
            sync_state=SyncState.SYNCED,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=self._eid(),
            present=True,
            version=1,
            is_logically_deleted=False,
        )
        assert svc.detect_and_resolve(local, remote, LocalWinsSyncConflictStrategy()) == (
            None,
            None,
        )
