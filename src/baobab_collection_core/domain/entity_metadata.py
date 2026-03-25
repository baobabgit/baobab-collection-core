"""Agrégat des métadonnées communes partagées par les futures entités."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.entity_lifecycle_state import EntityLifecycleState
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.validation_exception import ValidationException


@dataclass(frozen=True, slots=True)
class EntityMetadata:
    """Bundle immuable prêt à accompagner usager, carte, copie, contenant ou mutation.

    Combine horodatages, version optimiste, synchro et cycle de vie. Les mises à jour
    passent par des méthodes ``with_*`` pour préserver l'immuabilité.

    :ivar timestamps: Horodatages d'audit.
    :ivar version: Compteur de révision locale.
    :ivar sync_state: État dans le pipeline de synchronisation.
    :ivar lifecycle_state: Niveau de maturité métier.
    """

    timestamps: AuditTimestamps
    version: EntityVersion
    sync_state: SyncState
    lifecycle_state: EntityLifecycleState = EntityLifecycleState.ACTIVE

    def with_timestamps(self, timestamps: AuditTimestamps) -> EntityMetadata:
        """Remplace les horodatages en conservant version et états."""
        return replace(self, timestamps=timestamps)

    def with_version(self, version: EntityVersion) -> EntityMetadata:
        """Remplace la version (vérifier la monotonie côté appelant si nécessaire)."""
        return replace(self, version=version)

    def with_sync_state(self, sync_state: SyncState) -> EntityMetadata:
        """Met à jour l'état de synchronisation."""
        return replace(self, sync_state=sync_state)

    def with_lifecycle_state(self, lifecycle_state: EntityLifecycleState) -> EntityMetadata:
        """Met à jour le statut de cycle de vie."""
        return replace(self, lifecycle_state=lifecycle_state)

    def touch(self, moment: datetime, *, sync_state: SyncState | None = None) -> EntityMetadata:
        """Avance ``updated_at`` et ajuste optionnellement :class:`SyncState`.

        :param moment: Instant de modification.
        :param sync_state: Si fourni, remplace l'état de synchro (ex. ``DIRTY``).
        """
        new_ts = self.timestamps.with_updated_at(moment)
        meta = replace(self, timestamps=new_ts)
        if sync_state is not None:
            meta = replace(meta, sync_state=sync_state)
        return meta

    def bump_version(self, moment: datetime) -> EntityMetadata:
        """Incrémente la version optimiste et actualise ``updated_at``."""
        new_ts = self.timestamps.with_updated_at(moment)
        return replace(self, timestamps=new_ts, version=self.version.next())

    def mark_deleted(self, moment: datetime) -> EntityMetadata:
        """Soft-delete : horodatages, états ``DELETED``/``ARCHIVED``, version +1."""
        new_ts = self.timestamps.with_deleted_at(moment)
        return replace(
            self,
            timestamps=new_ts,
            version=self.version.next(),
            sync_state=SyncState.DELETED,
            lifecycle_state=EntityLifecycleState.ARCHIVED,
        )

    def require_monotone_version(self, previous: EntityVersion) -> None:
        """Vérifie que cette métadonnée ne régresse pas par rapport à ``previous``.

        :raises ValidationException: si ``self.version`` est strictement inférieure.
        """
        if self.version.value < previous.value:
            raise ValidationException(
                "La version des métadonnées ne peut pas diminuer par rapport à l'état connu."
            )

    def to_serializable(self) -> dict[str, object]:
        """Structure JSON-ready imbriquée."""
        return {
            "timestamps": self.timestamps.to_serializable(),
            "version": self.version.to_primitive(),
            "sync_state": self.sync_state.value,
            "lifecycle_state": self.lifecycle_state.value,
        }
