"""Tests unitaires pour :class:`Container`."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.container import Container
from baobab_collection_core.domain.container_kind import ContainerKind
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_lifecycle_state import EntityLifecycleState
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.container_cycle_exception import ContainerCycleException
from baobab_collection_core.exceptions.invalid_container_exception import InvalidContainerException


class TestContainer:
    """Règles métier locales des contenants."""

    @staticmethod
    def _now() -> datetime:
        return datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc)

    def _root(self, *, parent_id: DomainId | None = None) -> Container:
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        return Container.create(
            DomainId("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
            "Rangement A",
            ContainerKind.BOX,
            metadata,
            parent_id=parent_id,
        )

    def test_create_nominal(self) -> None:
        """Création avec nom normalisé."""
        c = self._root()
        assert c.name == "Rangement A"
        assert c.kind is ContainerKind.BOX
        assert c.parent_id is None
        assert c.is_archived is False

    def test_empty_name_raises(self) -> None:
        """Nom vide interdit."""
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        with pytest.raises(InvalidContainerException):
            Container.create(
                DomainId("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
                "  ",
                ContainerKind.STACK,
                metadata,
            )

    def test_update_bumps_version_when_changed(self) -> None:
        """Mutation synchronisée avec métadonnées."""
        c = self._root()
        later = c.metadata.timestamps.updated_at + timedelta(minutes=10)
        c.update(later, name="Boîte B")
        assert c.name == "Boîte B"
        assert c.metadata.version.value == 1
        assert c.metadata.sync_state.value == "dirty"

    def test_set_parent_no_op_same_parent(self) -> None:
        """Même parent : pas d'incrément inutile."""
        pid = DomainId("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
        c = self._root(parent_id=pid)
        before = c.metadata.version.value
        c.set_parent(c.metadata.timestamps.updated_at + timedelta(seconds=1), pid)
        assert c.metadata.version.value == before

    def test_self_parent_raises(self) -> None:
        """Auto-parent explicite refusé."""
        c = self._root()
        moment = c.metadata.timestamps.updated_at + timedelta(seconds=2)
        with pytest.raises(ContainerCycleException):
            c.set_parent(moment, c.entity_id)

    def test_archive_sets_lifecycle(self) -> None:
        """Archivage : cycle de vie archivé et synchro dirty."""
        c = self._root()
        moment = c.metadata.timestamps.updated_at + timedelta(hours=1)
        c.archive(moment)
        assert c.is_archived is True
        assert c.metadata.lifecycle_state is EntityLifecycleState.ARCHIVED
        assert c.metadata.sync_state.value == "dirty"

    def test_archive_twice_raises(self) -> None:
        """Archivage idempotent interdit."""
        c = self._root()
        moment = c.metadata.timestamps.updated_at + timedelta(hours=1)
        c.archive(moment)
        with pytest.raises(InvalidContainerException):
            c.archive(moment + timedelta(seconds=1))

    def test_mutations_forbidden_after_archive(self) -> None:
        """Contenant archivé : plus de mise à jour ni de reparentage."""
        c = self._root()
        moment = c.metadata.timestamps.updated_at + timedelta(hours=1)
        c.archive(moment)
        with pytest.raises(InvalidContainerException):
            c.update(moment + timedelta(seconds=5), name="X")
        with pytest.raises(InvalidContainerException):
            c.set_parent(moment + timedelta(seconds=6), None)
