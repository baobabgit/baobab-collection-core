"""Tests pour :class:`EntityMetadata`."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.entity_lifecycle_state import EntityLifecycleState
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions import ValidationException


class TestEntityMetadata:
    """Orchestration des value objects de métadonnées."""

    @staticmethod
    def _base_metadata() -> EntityMetadata:
        moment = datetime(2024, 5, 1, 8, 30, tzinfo=timezone.utc)
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        return EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )

    def test_touch_updates_timestamp_and_optional_sync(self) -> None:
        """touch() déplace updated_at et peut marquer DIRTY."""
        meta = self._base_metadata()
        new_moment = meta.timestamps.updated_at + timedelta(minutes=5)
        touched = meta.touch(new_moment, sync_state=SyncState.DIRTY)
        assert touched.sync_state is SyncState.DIRTY
        assert touched.timestamps.updated_at == new_moment
        assert touched.version.value == 0

    def test_touch_without_sync_preserves_state(self) -> None:
        """touch() peut se limiter à déplacer l'horodatage."""
        meta = self._base_metadata()
        new_moment = meta.timestamps.updated_at + timedelta(minutes=1)
        touched = meta.touch(new_moment)
        assert touched.sync_state is meta.sync_state
        assert touched.timestamps.updated_at == new_moment

    def test_bump_version_increments_and_moves_timestamp(self) -> None:
        """bump_version() combine temporalité + optimistic lock."""
        meta = self._base_metadata()
        new_moment = meta.timestamps.updated_at + timedelta(hours=1)
        bumped = meta.bump_version(new_moment)
        assert bumped.version.value == 1
        assert bumped.timestamps.updated_at == new_moment

    def test_mark_deleted_sets_states_and_version(self) -> None:
        """Soft delete harmonise synchro et cycle de vie."""
        meta = self._base_metadata()
        moment = meta.timestamps.updated_at + timedelta(days=1)
        deleted = meta.mark_deleted(moment)
        assert deleted.sync_state is SyncState.DELETED
        assert deleted.lifecycle_state is EntityLifecycleState.ARCHIVED
        assert deleted.timestamps.deleted_at == moment
        assert deleted.version.value == 1

    def test_require_monotone_version_accepts_equal_or_greater(self) -> None:
        """Pas d'exception si la version progresse."""
        base = self._base_metadata()
        moment = base.timestamps.updated_at + timedelta(seconds=5)
        newer = base.bump_version(moment)
        newer.require_monotone_version(base.version)

    def test_require_monotone_version_rejects_regression(self) -> None:
        """Régression de version détectée."""
        base = self._base_metadata()
        moment = base.timestamps.updated_at + timedelta(seconds=2)
        advanced = base.bump_version(moment)
        regressed = advanced.with_version(EntityVersion(0))
        with pytest.raises(ValidationException):
            regressed.require_monotone_version(advanced.version)

    def test_to_serializable_nested(self) -> None:
        """Structure imbriquée pour transports simples."""
        meta = self._base_metadata()
        blob = meta.to_serializable()
        assert blob["sync_state"] == SyncState.CLEAN.value
        assert blob["version"] == 0

    def test_with_timestamps_and_lifecycle_mutations(self) -> None:
        """Mutations ciblées sans toucher au reste."""
        meta = self._base_metadata()
        moment = meta.timestamps.updated_at + timedelta(seconds=30)
        new_stamps = meta.timestamps.with_updated_at(moment)
        touched = meta.with_timestamps(new_stamps).with_lifecycle_state(
            EntityLifecycleState.DRAFT,
        )
        assert touched.lifecycle_state is EntityLifecycleState.DRAFT
        assert touched.timestamps.updated_at == moment

    def test_with_sync_state_and_with_version(self) -> None:
        """Ajustements fins de synchro et de version."""
        meta = self._base_metadata()
        retagged = meta.with_sync_state(SyncState.CONFLICT).with_version(EntityVersion(4))
        assert retagged.sync_state is SyncState.CONFLICT
        assert retagged.version.value == 4
