"""Tests du cœur de synchronisation sans transport."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.application.sync_core_service import SyncCoreService
from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.sync_delta_kind import SyncDeltaKind
from baobab_collection_core.domain.sync_dtos import (
    EntitySyncApplyRecord,
    LocalEntitySyncSnapshot,
    RemoteEntitySyncSnapshot,
)
from baobab_collection_core.domain.sync_plan_action import SyncPlanAction
from baobab_collection_core.domain.sync_session_outcome import SyncSessionOutcome
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.invalid_sync_snapshot_exception import (
    InvalidSyncSnapshotException,
)
from tests.baobab_collection_core.support.fake_remote_entity_sync_snapshot import (
    FakeRemoteEntitySyncSnapshotProvider,
)


class TestSyncCoreService:  # pylint: disable=too-many-public-methods
    """Comparaison, plan, application et consolidation."""

    @staticmethod
    def _moment() -> datetime:
        return datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc)

    @staticmethod
    def _eid(n: str = "01") -> DomainId:
        return DomainId(f"50000000-0000-4000-8000-0000000000{n}")

    def _local(
        self,
        *,
        version: int,
        sync_state: SyncState,
        deleted: bool = False,
        kind: LocalEntityKind = LocalEntityKind.PHYSICAL_COPY,
        eid: DomainId | None = None,
    ) -> LocalEntitySyncSnapshot:
        return LocalEntitySyncSnapshot(
            entity_id=eid if eid is not None else self._eid(),
            entity_kind=kind,
            version=version,
            sync_state=sync_state,
            is_logically_deleted=deleted,
        )

    def _remote(
        self,
        *,
        present: bool,
        version: int,
        deleted: bool = False,
        eid: DomainId | None = None,
    ) -> RemoteEntitySyncSnapshot:
        return RemoteEntitySyncSnapshot(
            entity_id=eid if eid is not None else self._eid(),
            present=present,
            version=version,
            is_logically_deleted=deleted,
        )

    def test_compare_push_when_local_dirty_remote_absent(self) -> None:
        """Détection PUSH : travail local, rien côté pair."""
        svc = SyncCoreService()
        delta = svc.compare(
            self._local(version=1, sync_state=SyncState.DIRTY),
            self._remote(present=False, version=0),
        )
        assert delta.kind is SyncDeltaKind.PUSH

    def test_compare_pull_when_remote_ahead_clean_local(self) -> None:
        """PULL si distant plus récent et local propre."""
        svc = SyncCoreService()
        delta = svc.compare(
            self._local(version=1, sync_state=SyncState.SYNCED),
            self._remote(present=True, version=3),
        )
        assert delta.kind is SyncDeltaKind.PULL

    def test_compare_conflict_when_remote_ahead_and_local_dirty(self) -> None:
        """Conflit : divergences simultanées."""
        svc = SyncCoreService()
        delta = svc.compare(
            self._local(version=1, sync_state=SyncState.DIRTY),
            self._remote(present=True, version=4),
        )
        assert delta.kind is SyncDeltaKind.CONFLICT

    def test_compare_none_when_aligned(self) -> None:
        """Aucun écart : versions égales, local clean."""
        svc = SyncCoreService()
        delta = svc.compare(
            self._local(version=2, sync_state=SyncState.SYNCED),
            self._remote(present=True, version=2),
        )
        assert delta.kind is SyncDeltaKind.NONE

    def test_compare_push_when_local_ahead(self) -> None:
        """Local plus récent : propagation attendue."""
        svc = SyncCoreService()
        delta = svc.compare(
            self._local(version=4, sync_state=SyncState.SYNCED),
            self._remote(present=True, version=2),
        )
        assert delta.kind is SyncDeltaKind.PUSH

    def test_negative_local_version_raises(self) -> None:
        """Garde-fou sur instantané local."""
        svc = SyncCoreService()
        with pytest.raises(InvalidSyncSnapshotException):
            svc.compare(
                self._local(version=-1, sync_state=SyncState.DIRTY),
                self._remote(present=False, version=0),
            )

    def test_negative_remote_version_when_present_raises(self) -> None:
        """Version distante incohérente si présent."""
        svc = SyncCoreService()
        with pytest.raises(InvalidSyncSnapshotException):
            svc.compare(
                self._local(version=1, sync_state=SyncState.SYNCED),
                self._remote(present=True, version=-1),
            )

    def test_compare_both_deleted_none(self) -> None:
        """Deux tombes alignées : rien à faire."""
        svc = SyncCoreService()
        eid = self._eid()
        delta = svc.compare(
            self._local(version=2, sync_state=SyncState.DELETED, deleted=True, eid=eid),
            self._remote(present=True, version=2, deleted=True, eid=eid),
        )
        assert delta.kind is SyncDeltaKind.NONE

    def test_build_plan_maps_actions(self) -> None:
        """Génération de plan déterministe."""
        svc = SyncCoreService()
        e1 = self._eid("01")
        e2 = self._eid("02")
        d1 = svc.compare(
            self._local(version=0, sync_state=SyncState.DIRTY, eid=e1),
            self._remote(present=False, version=0, eid=e1),
        )
        d2 = svc.compare(
            self._local(
                version=1, sync_state=SyncState.SYNCED, kind=LocalEntityKind.CONTAINER, eid=e2
            ),
            self._remote(present=True, version=5, eid=e2),
        )
        plan = svc.build_plan((d1, d2), plan_id="plan-x")
        assert plan.plan_id == "plan-x"
        actions = {i.action for i in plan.items}
        assert SyncPlanAction.PUSH in actions
        assert SyncPlanAction.PULL in actions

    def test_consolidate_conflict_wins(self) -> None:
        """Agrégat session : conflit prioritaire."""
        records = (
            EntitySyncApplyRecord(self._eid(), SyncSessionOutcome.SYNCED),
            EntitySyncApplyRecord(self._eid("02"), SyncSessionOutcome.CONFLICT),
        )
        assert SyncCoreService.consolidate_session_outcome(records) is SyncSessionOutcome.CONFLICT

    def test_consolidate_all_synced(self) -> None:
        """Session entièrement verte."""
        records = (
            EntitySyncApplyRecord(self._eid(), SyncSessionOutcome.SYNCED),
            EntitySyncApplyRecord(self._eid("02"), SyncSessionOutcome.SYNCED),
        )
        assert SyncCoreService.consolidate_session_outcome(records) is SyncSessionOutcome.SYNCED

    def test_consolidate_error_over_pending(self) -> None:
        """Erreur avant pending."""
        records = (
            EntitySyncApplyRecord(self._eid(), SyncSessionOutcome.PENDING),
            EntitySyncApplyRecord(self._eid("02"), SyncSessionOutcome.SYNC_ERROR),
        )
        assert SyncCoreService.consolidate_session_outcome(records) is SyncSessionOutcome.SYNC_ERROR

    def test_build_batch_result(self) -> None:
        """Résultat de batch enveloppe la consolidation."""
        svc = SyncCoreService()
        rec = (EntitySyncApplyRecord(self._eid(), SyncSessionOutcome.SYNCED),)
        batch = svc.build_batch_result(rec)
        assert batch.session_outcome is SyncSessionOutcome.SYNCED
        assert batch.records == rec

    def test_apply_metadata_synced_without_remote_version(self) -> None:
        """Succès sans révision distante explicite : alignement SYNCED."""
        moment = self._moment()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        meta = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(3),
            sync_state=SyncState.DIRTY,
        )
        new_meta = SyncCoreService.apply_entity_outcome_to_metadata(
            meta,
            SyncSessionOutcome.SYNCED,
            moment + timedelta(seconds=5),
        )
        assert new_meta.sync_state is SyncState.SYNCED
        assert new_meta.version.value == 3

    def test_apply_metadata_conflict_and_pending(self) -> None:
        """CONFLICT et PENDING mappés sur SyncState."""
        moment = self._moment()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        base = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(1),
            sync_state=SyncState.DIRTY,
        )
        conf = SyncCoreService.apply_entity_outcome_to_metadata(
            base,
            SyncSessionOutcome.CONFLICT,
            moment + timedelta(seconds=1),
        )
        assert conf.sync_state is SyncState.CONFLICT
        pend = SyncCoreService.apply_entity_outcome_to_metadata(
            base,
            SyncSessionOutcome.PENDING,
            moment + timedelta(seconds=2),
        )
        assert pend.sync_state is SyncState.DIRTY

    def test_apply_metadata_synced_with_version(self) -> None:
        """Application succès : version distante et SYNCED."""
        moment = self._moment()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        meta = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(2),
            sync_state=SyncState.DIRTY,
        )
        new_meta = SyncCoreService.apply_entity_outcome_to_metadata(
            meta,
            SyncSessionOutcome.SYNCED,
            moment + timedelta(minutes=1),
            confirmed_remote_version=5,
        )
        assert new_meta.sync_state is SyncState.SYNCED
        assert new_meta.version.value == 5

    def test_apply_metadata_sync_error(self) -> None:
        """Erreur retentable sur métadonnées."""
        moment = self._moment()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        meta = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(1),
            sync_state=SyncState.DIRTY,
        )
        new_meta = SyncCoreService.apply_entity_outcome_to_metadata(
            meta,
            SyncSessionOutcome.SYNC_ERROR,
            moment + timedelta(seconds=30),
        )
        assert new_meta.sync_state is SyncState.SYNC_ERROR

    def test_apply_metadata_version_regression_raises(self) -> None:
        """Version distante incohérente."""
        moment = self._moment()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        meta = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(5),
            sync_state=SyncState.DIRTY,
        )
        with pytest.raises(InvalidSyncSnapshotException):
            SyncCoreService.apply_entity_outcome_to_metadata(
                meta,
                SyncSessionOutcome.SYNCED,
                moment,
                confirmed_remote_version=3,
            )

    def test_fetch_and_compare_uses_port(self) -> None:
        """Port distant injecté."""
        eid = self._eid()
        kind = LocalEntityKind.COLLECTION_CARD
        remote_snap = RemoteEntitySyncSnapshot(
            entity_id=eid,
            present=True,
            version=2,
            is_logically_deleted=False,
        )
        fake = FakeRemoteEntitySyncSnapshotProvider()
        fake.seed(remote_snap, kind)
        svc = SyncCoreService(remote=fake)
        local = LocalEntitySyncSnapshot(
            entity_id=eid,
            entity_kind=kind,
            version=2,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        d = svc.fetch_and_compare(local)
        assert d.kind is SyncDeltaKind.PUSH

    def test_fetch_without_port_raises(self) -> None:
        """Garde-fou sans adaptateur."""
        svc = SyncCoreService()
        with pytest.raises(InvalidSyncSnapshotException):
            svc.fetch_and_compare(
                LocalEntitySyncSnapshot(
                    entity_id=self._eid(),
                    entity_kind=LocalEntityKind.COLLECTION_USER,
                    version=0,
                    sync_state=SyncState.DIRTY,
                    is_logically_deleted=False,
                )
            )

    def test_mismatched_entity_ids_raise(self) -> None:
        """Paire incohérente."""
        svc = SyncCoreService()
        local = LocalEntitySyncSnapshot(
            entity_id=DomainId("60000000-0000-4000-8000-000000000001"),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            version=0,
            sync_state=SyncState.SYNCED,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=DomainId("60000000-0000-4000-8000-000000000002"),
            present=True,
            version=1,
            is_logically_deleted=False,
        )
        with pytest.raises(InvalidSyncSnapshotException):
            svc.compare(local, remote)
