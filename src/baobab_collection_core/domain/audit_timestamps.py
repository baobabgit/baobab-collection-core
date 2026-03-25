"""Horodatages de création, mise à jour et suppression logique."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone

from baobab_collection_core.exceptions.validation_exception import ValidationException


def _require_utc(field_name: str, moment: datetime) -> None:
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValidationException(
            f"{field_name} doit être timezone-aware (recommandé : datetime.timezone.utc)."
        )


@dataclass(frozen=True, slots=True)
class AuditTimestamps:
    """Value object immuable pour tracer les instants clés d'une entité.

    Tous les :class:`datetime` doivent être conscients du fuseau (UTC conseillé).

    :ivar created_at: Instant de création logique.
    :ivar updated_at: Dernière modification métier significative.
    :ivar deleted_at: Instant de suppression logique, ou ``None`` si actif.
    """

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        _require_utc("created_at", self.created_at)
        _require_utc("updated_at", self.updated_at)
        if self.deleted_at is not None:
            _require_utc("deleted_at", self.deleted_at)
        if self.updated_at < self.created_at:
            raise ValidationException("updated_at ne peut précéder created_at.")
        if self.deleted_at is not None and self.deleted_at < self.updated_at:
            raise ValidationException("deleted_at ne peut précéder updated_at.")

    def with_updated_at(self, moment: datetime) -> AuditTimestamps:
        """Nouvel enregistrement d'horodatages avec ``updated_at`` déplacé.

        :param moment:
            Nouvel instant de mise à jour (>= ``created_at``, <= ``deleted_at`` si défini).
        :returns: Copie immuable mise à jour.
        """
        _require_utc("updated_at", moment)
        if moment < self.created_at:
            raise ValidationException("updated_at ne peut précéder created_at.")
        if self.deleted_at is not None and moment > self.deleted_at:
            raise ValidationException("updated_at ne peut suivre deleted_at lorsque défini.")
        return replace(self, updated_at=moment)

    def with_deleted_at(self, moment: datetime) -> AuditTimestamps:
        """Marque la suppression logique en alignant ``updated_at`` et ``deleted_at``.

        :param moment: Instant unique appliqué à la fin de vie locale.
        """
        _require_utc("deleted_at", moment)
        if moment < self.updated_at:
            raise ValidationException("deleted_at ne peut précéder updated_at.")
        return replace(self, updated_at=moment, deleted_at=moment)

    def ensure_utc_naive_safe_copy(self) -> AuditTimestamps:
        """Normalise en UTC pour comparaisons/sérialisation cohérentes.

        :returns: Copie avec les instants convertis via ``astimezone(UTC)``.
        """
        created = self.created_at.astimezone(timezone.utc)
        updated = self.updated_at.astimezone(timezone.utc)
        deleted = self.deleted_at.astimezone(timezone.utc) if self.deleted_at is not None else None
        return replace(self, created_at=created, updated_at=updated, deleted_at=deleted)

    def to_serializable(self) -> dict[str, str | None]:
        """Représentation dict avec ISO 8601 (UTC)."""
        stamps = self.ensure_utc_naive_safe_copy()
        return {
            "created_at": stamps.created_at.isoformat(),
            "updated_at": stamps.updated_at.isoformat(),
            "deleted_at": stamps.deleted_at.isoformat() if stamps.deleted_at else None,
        }
