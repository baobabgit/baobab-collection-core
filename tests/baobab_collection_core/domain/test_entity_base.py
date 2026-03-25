"""Tests pour :class:`EntityBase`."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.domain import (
    AuditTimestamps,
    DomainId,
    EntityBase,
    EntityMetadata,
    EntityVersion,
    SyncState,
)
from baobab_collection_core.exceptions import ValidationException


class SampleEntity(EntityBase):
    """Double de test minimal pour l'ABC :class:`EntityBase`."""

    __slots__ = ()


class TestEntityBase:
    """Garde-fous sur le remplacement de métadonnées."""

    @staticmethod
    def _metadata(version: int = 0) -> EntityMetadata:
        moment = datetime(2025, 1, 1, tzinfo=timezone.utc)
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        return EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(version),
            sync_state=SyncState.CLEAN,
        )

    def test_properties_expose_value_objects(self) -> None:
        """Identifiant et métadonnées restent typés."""
        meta = self._metadata()
        entity_id = DomainId(str(uuid.uuid4()))
        entity = SampleEntity(entity_id, meta)
        assert entity.entity_id == entity_id
        assert entity.metadata is meta

    def test_replace_metadata_rejects_version_regression(self) -> None:
        """Cohérence optimistic concurrency côté entité."""
        entity = SampleEntity(DomainId(str(uuid.uuid4())), self._metadata(2))
        stale = entity.metadata.with_version(EntityVersion(1))
        with pytest.raises(ValidationException):
            entity.replace_metadata(stale)

    def test_replace_metadata_accepts_progression(self) -> None:
        """Mise à jour monotone autorisée."""
        entity = SampleEntity(DomainId(str(uuid.uuid4())), self._metadata(1))
        moment = entity.metadata.timestamps.updated_at + timedelta(minutes=1)
        advanced = entity.metadata.bump_version(moment)
        entity.replace_metadata(advanced)
        assert entity.metadata.version.value == 2
