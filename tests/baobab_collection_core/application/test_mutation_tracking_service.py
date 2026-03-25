"""Tests du service de suivi des mutations offline-first."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.application.mutation_tracking_service import MutationTrackingService
from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.local_mutation_kind import LocalMutationKind
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions import (
    InvalidLocalMutationException,
    MutationNotFoundException,
)
from tests.baobab_collection_core.support.in_memory_local_mutation_journal import (
    InMemoryLocalMutationJournal,
)


class TestMutationTrackingService:
    """Journal, extraction et accusés."""

    @staticmethod
    def _moment() -> datetime:
        return datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)

    def _svc(self) -> tuple[MutationTrackingService, InMemoryLocalMutationJournal]:
        journal = InMemoryLocalMutationJournal()
        return MutationTrackingService(journal), journal

    def _meta(self, version: int = 0, sync: SyncState = SyncState.DIRTY) -> EntityMetadata:
        m = self._moment()
        stamps = AuditTimestamps(created_at=m, updated_at=m)
        return EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(version),
            sync_state=sync,
        )

    def test_record_mutation_then_list_pending(self) -> None:
        """Enregistrement puis lecture des attentes."""
        svc, _ = self._svc()
        eid = DomainId("30000000-0000-4000-8000-000000000001")
        m = svc.record_local_mutation(
            entity_kind=LocalEntityKind.COLLECTION_CARD,
            entity_id=eid,
            kind=LocalMutationKind.UPDATE,
            recorded_at=self._moment(),
            entity_version_at_record=3,
            sync_state_at_record=SyncState.DIRTY,
            payload_hints=(("field", "name"),),
        )
        pending = svc.extract_pending_changes()
        assert len(pending) == 1
        assert pending[0].mutation_id == m.mutation_id
        assert pending[0].entity_version_at_record == 3
        assert pending[0].payload_hints == (("field", "name"),)

    def test_soft_delete_mutation_captures_deleted_sync_state(self) -> None:
        """Suppression logique : instantané DELETED dans le journal."""
        svc, _ = self._svc()
        meta = self._meta(version=4, sync=SyncState.DELETED)
        entry = svc.record_from_entity_snapshot(
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            entity_id=DomainId("30000000-0000-4000-8000-000000000099"),
            kind=LocalMutationKind.SOFT_DELETE,
            metadata=meta,
            recorded_at=self._moment(),
        )
        assert entry.sync_state_at_record is SyncState.DELETED
        assert entry.kind is LocalMutationKind.SOFT_DELETE

    def test_acknowledge_removes_from_pending_extract(self) -> None:
        """Accusé : plus listé dans les changements en attente."""
        svc, _ = self._svc()
        eid = DomainId("30000000-0000-4000-8000-000000000002")
        m1id = DomainId("40000000-0000-4000-8000-000000000001")
        m2id = DomainId("40000000-0000-4000-8000-000000000002")
        m1 = svc.record_local_mutation(
            entity_kind=LocalEntityKind.CONTAINER,
            entity_id=eid,
            kind=LocalMutationKind.MOVE,
            recorded_at=self._moment(),
            entity_version_at_record=1,
            sync_state_at_record=SyncState.DIRTY,
            mutation_id=m1id,
        )
        m2 = svc.record_local_mutation(
            entity_kind=LocalEntityKind.CONTAINER,
            entity_id=eid,
            kind=LocalMutationKind.ATTACH,
            recorded_at=self._moment() + timedelta(seconds=1),
            entity_version_at_record=2,
            sync_state_at_record=SyncState.DIRTY,
            mutation_id=m2id,
        )
        svc.acknowledge_mutations([m1.mutation_id])
        rest = svc.list_pending_mutations()
        assert len(rest) == 1
        assert rest[0].mutation_id == m2.mutation_id
        svc.acknowledge_mutations([m2.mutation_id])
        assert svc.pending_mutation_count() == 0

    def test_acknowledge_unknown_raises(self) -> None:
        """Identifiant de mutation inconnu."""
        svc, _ = self._svc()
        with pytest.raises(MutationNotFoundException):
            svc.acknowledge_mutations([DomainId("99999999-9999-4999-8999-999999999999")])

    def test_acknowledge_twice_raises(self) -> None:
        """Double accusé interdit."""
        svc, _ = self._svc()
        mid = DomainId("40000000-0000-4000-8000-000000000010")
        svc.record_local_mutation(
            entity_kind=LocalEntityKind.COLLECTION_USER,
            entity_id=DomainId("30000000-0000-4000-8000-000000000010"),
            kind=LocalMutationKind.CREATE,
            recorded_at=self._moment(),
            entity_version_at_record=0,
            sync_state_at_record=SyncState.DIRTY,
            mutation_id=mid,
        )
        svc.acknowledge_mutations([mid])
        with pytest.raises(InvalidLocalMutationException):
            svc.acknowledge_mutations([mid])

    def test_acknowledge_all_for_entity(self) -> None:
        """Accusé groupé par entité cible."""
        svc, _ = self._svc()
        eid = DomainId("30000000-0000-4000-8000-000000000030")
        svc.record_local_mutation(
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            entity_id=eid,
            kind=LocalMutationKind.DETACH,
            recorded_at=self._moment(),
            entity_version_at_record=1,
            sync_state_at_record=SyncState.DIRTY,
            mutation_id=DomainId("40000000-0000-4000-8000-000000000030"),
        )
        svc.record_local_mutation(
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            entity_id=eid,
            kind=LocalMutationKind.UPDATE,
            recorded_at=self._moment() + timedelta(seconds=2),
            entity_version_at_record=2,
            sync_state_at_record=SyncState.DIRTY,
            mutation_id=DomainId("40000000-0000-4000-8000-000000000031"),
        )
        n = svc.acknowledge_all_pending_for_entity(eid)
        assert n == 2
        assert svc.pending_mutation_count() == 0

    def test_record_from_entity_snapshot_coherence(self) -> None:
        """Le journal reflète la version et le sync state du metadata passé."""
        svc, _ = self._svc()
        meta = self._meta(version=5, sync=SyncState.CONFLICT)
        entry = svc.record_from_entity_snapshot(
            entity_kind=LocalEntityKind.COLLECTION_CARD,
            entity_id=DomainId("30000000-0000-4000-8000-000000000040"),
            kind=LocalMutationKind.UPDATE,
            metadata=meta,
            recorded_at=self._moment(),
        )
        assert entry.entity_version_at_record == 5
        assert entry.sync_state_at_record is SyncState.CONFLICT

    def test_suggested_sync_state_helpers(self) -> None:
        """Helpers de transition sans transport."""
        meta = self._meta(version=1, sync=SyncState.DIRTY)
        later = self._moment() + timedelta(minutes=1)
        synced = MutationTrackingService.suggested_metadata_after_successful_push(meta, later)
        assert synced.sync_state is SyncState.SYNCED
        conflict = MutationTrackingService.suggested_metadata_mark_conflict(meta, later)
        assert conflict.sync_state is SyncState.CONFLICT

    def test_negative_entity_version_rejected(self) -> None:
        """Version d'entité négative interdite."""
        svc, _ = self._svc()
        with pytest.raises(InvalidLocalMutationException):
            svc.record_local_mutation(
                entity_kind=LocalEntityKind.COLLECTION_CARD,
                entity_id=DomainId("30000000-0000-4000-8000-000000000055"),
                kind=LocalMutationKind.UPDATE,
                recorded_at=self._moment(),
                entity_version_at_record=-1,
                sync_state_at_record=SyncState.DIRTY,
            )

    def test_payload_validation(self) -> None:
        """Taille et clés du payload limitées."""
        svc, _ = self._svc()
        with pytest.raises(InvalidLocalMutationException):
            svc.record_local_mutation(
                entity_kind=LocalEntityKind.CONTAINER,
                entity_id=DomainId("30000000-0000-4000-8000-000000000050"),
                kind=LocalMutationKind.UPDATE,
                recorded_at=self._moment(),
                entity_version_at_record=0,
                sync_state_at_record=SyncState.DIRTY,
                payload_hints=(("", "x"),),
            )

    def test_duplicate_mutation_id_rejected(self) -> None:
        """Identifiant de mutation unique."""
        svc, _ = self._svc()
        mid = DomainId("40000000-0000-4000-8000-000000000060")
        eid = DomainId("30000000-0000-4000-8000-000000000060")
        svc.record_local_mutation(
            entity_kind=LocalEntityKind.CONTAINER,
            entity_id=eid,
            kind=LocalMutationKind.CREATE,
            recorded_at=self._moment(),
            entity_version_at_record=0,
            sync_state_at_record=SyncState.DIRTY,
            mutation_id=mid,
        )
        with pytest.raises(InvalidLocalMutationException):
            svc.record_local_mutation(
                entity_kind=LocalEntityKind.CONTAINER,
                entity_id=eid,
                kind=LocalMutationKind.CREATE,
                recorded_at=self._moment(),
                entity_version_at_record=0,
                sync_state_at_record=SyncState.DIRTY,
                mutation_id=mid,
            )
