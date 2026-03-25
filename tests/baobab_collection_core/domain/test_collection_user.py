"""Tests unitaires de :class:`CollectionUser`."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.collection_user import CollectionUser
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions import InvalidUserException


class TestCollectionUser:
    """Validations, mutations et cohérence de version / synchro."""

    @staticmethod
    def _now() -> datetime:
        return datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc)

    def _fresh_user(self, *, name: str = "Alice") -> CollectionUser:
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        return CollectionUser.create(
            DomainId("00000000-0000-4000-8000-000000000001"), name, metadata
        )

    def test_create_rejects_blank_name(self) -> None:
        """Nom vide interdit."""
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        with pytest.raises(InvalidUserException):
            CollectionUser.create(
                DomainId("00000000-0000-4000-8000-000000000002"),
                "   ",
                metadata,
            )

    def test_update_display_name_bumps_version_and_marks_dirty(self) -> None:
        """Chaque mutation avance la version et marque DIRTY."""
        user = self._fresh_user()
        moment = user.metadata.timestamps.updated_at + timedelta(minutes=5)
        user.update_display_name("Alice Martin", moment)
        assert user.display_name == "Alice Martin"
        assert user.metadata.version.value == 1
        assert user.metadata.sync_state.value == "dirty"

    def test_deactivate_marks_inactive_and_dirty(self) -> None:
        """Désactivation sans destruction physique."""
        user = self._fresh_user()
        moment = user.metadata.timestamps.updated_at + timedelta(hours=1)
        user.deactivate(moment)
        assert user.is_active is False
        assert user.metadata.sync_state.value == "dirty"
        assert user.metadata.version.value == 1

    def test_double_deactivate_rejected(self) -> None:
        """Transition idempotente interdite explicitement."""
        user = self._fresh_user()
        moment = user.metadata.timestamps.updated_at + timedelta(minutes=1)
        user.deactivate(moment)
        with pytest.raises(InvalidUserException):
            user.deactivate(moment + timedelta(minutes=1))

    def test_display_name_max_length(self) -> None:
        """Garde-fou de taille sur le libellé."""
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        long_name = "x" * 257
        with pytest.raises(InvalidUserException):
            CollectionUser.create(
                DomainId("00000000-0000-4000-8000-000000000003"),
                long_name,
                metadata,
            )
