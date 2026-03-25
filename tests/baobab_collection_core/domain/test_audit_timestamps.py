"""Tests pour :class:`AuditTimestamps`."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.exceptions import ValidationException


class TestAuditTimestamps:
    """Règles temporelles et immuabilité."""

    @staticmethod
    def _t0() -> datetime:
        return datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)

    def test_naive_datetime_rejected(self) -> None:
        """Exiger des instants timezone-aware."""
        naive = datetime(2024, 1, 1)
        with pytest.raises(ValidationException):
            AuditTimestamps(created_at=naive, updated_at=naive)

    def test_updated_before_created_rejected(self) -> None:
        """Invariant temporal de base."""
        created = self._t0()
        updated = created - timedelta(seconds=1)
        with pytest.raises(ValidationException):
            AuditTimestamps(created_at=created, updated_at=updated)

    def test_deleted_before_updated_rejected(self) -> None:
        """Soft delete doit suivre la dernière mise à jour connue."""
        created = self._t0()
        updated = created + timedelta(seconds=1)
        deleted = updated - timedelta(seconds=1)
        with pytest.raises(ValidationException):
            AuditTimestamps(created_at=created, updated_at=updated, deleted_at=deleted)

    def test_with_updated_at_advances(self) -> None:
        """Mutation fonctionnelle sur updated_at."""
        created = self._t0()
        stamps = AuditTimestamps(created_at=created, updated_at=created)
        new_updated = created + timedelta(seconds=5)
        advanced = stamps.with_updated_at(new_updated)
        assert advanced.updated_at == new_updated
        assert advanced.created_at == created

    def test_with_updated_at_before_created_rejected(self) -> None:
        """with_updated_at doit respecter created_at."""
        created = self._t0()
        stamps = AuditTimestamps(created_at=created, updated_at=created)
        with pytest.raises(ValidationException):
            stamps.with_updated_at(created - timedelta(seconds=1))

    def test_with_updated_at_cannot_cross_deleted(self) -> None:
        """updated_at ne peut pas dépasser deleted_at."""
        created = self._t0()
        updated = created + timedelta(seconds=1)
        deleted = updated + timedelta(seconds=1)
        stamps = AuditTimestamps(created_at=created, updated_at=updated, deleted_at=deleted)
        with pytest.raises(ValidationException):
            stamps.with_updated_at(deleted + timedelta(seconds=1))

    def test_with_deleted_at_sets_pair(self) -> None:
        """Suppression aligne updated/deleted au même instant."""
        created = self._t0()
        updated = created + timedelta(seconds=10)
        stamps = AuditTimestamps(created_at=created, updated_at=updated)
        moment = updated + timedelta(seconds=2)
        soft = stamps.with_deleted_at(moment)
        assert soft.deleted_at == moment
        assert soft.updated_at == moment

    def test_with_deleted_at_before_updated_rejected(self) -> None:
        """with_deleted_at ne peut avancer avant updated_at."""
        created = self._t0()
        updated = created + timedelta(seconds=5)
        stamps = AuditTimestamps(created_at=created, updated_at=updated)
        with pytest.raises(ValidationException):
            stamps.with_deleted_at(updated - timedelta(seconds=1))

    def test_to_serializable_iso8601(self) -> None:
        """Sortie JSON avec ISO8601."""
        created = self._t0()
        payload = AuditTimestamps(created_at=created, updated_at=created).to_serializable()
        assert payload["deleted_at"] is None
        created_str = payload["created_at"]
        assert created_str is not None
        assert created_str.endswith("+00:00")

    def test_ensure_utc_converts_offsets(self) -> None:
        """La normalisation UTC permet des comparaisons stables."""
        offset_tz = timezone(timedelta(hours=2))
        local = datetime(2024, 6, 1, 14, 0, tzinfo=offset_tz)
        stamps = AuditTimestamps(created_at=local, updated_at=local)
        normalized = stamps.ensure_utc_naive_safe_copy()
        assert normalized.created_at.tzinfo is timezone.utc
