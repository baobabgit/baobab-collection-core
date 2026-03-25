"""Tests pour :class:`LocalMutation`."""

from datetime import datetime, timezone

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.local_mutation import LocalMutation
from baobab_collection_core.domain.local_mutation_kind import LocalMutationKind
from baobab_collection_core.domain.sync_state import SyncState


class TestLocalMutation:
    """Journal unitaire et transitions d'état local."""

    def test_with_acknowledged_flips_pending(self) -> None:
        """Accusé de synchro : plus en attente."""
        moment = datetime(2026, 6, 1, 8, 0, tzinfo=timezone.utc)
        mid = DomainId("10000000-0000-4000-8000-000000000001")
        eid = DomainId("20000000-0000-4000-8000-000000000001")
        m = LocalMutation(
            mutation_id=mid,
            entity_kind=LocalEntityKind.CONTAINER,
            entity_id=eid,
            kind=LocalMutationKind.MOVE,
            recorded_at=moment,
            entity_version_at_record=2,
            sync_state_at_record=SyncState.DIRTY,
        )
        done = m.with_acknowledged()
        assert m.is_pending is True
        assert done.is_pending is False

    def test_to_serializable(self) -> None:
        """Export JSON-friendly."""
        moment = datetime(2026, 6, 1, 8, 0, tzinfo=timezone.utc)
        m = LocalMutation(
            mutation_id=DomainId("10000000-0000-4000-8000-000000000002"),
            entity_kind=LocalEntityKind.PHYSICAL_COPY,
            entity_id=DomainId("20000000-0000-4000-8000-000000000002"),
            kind=LocalMutationKind.ATTACH,
            recorded_at=moment,
            entity_version_at_record=1,
            sync_state_at_record=SyncState.DIRTY,
            payload_hints=(("container_id", "aaa"),),
        )
        blob = m.to_serializable()
        assert blob["kind"] == "attach"
        assert blob["payload_hints"] == {"container_id": "aaa"}
