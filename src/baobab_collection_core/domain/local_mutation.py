"""Enregistrement immutable d'une mutation locale en attente de synchronisation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.local_mutation_kind import LocalMutationKind
from baobab_collection_core.domain.sync_state import SyncState


@dataclass(frozen=True, slots=True)
class LocalMutation:  # pylint: disable=too-many-instance-attributes
    """Une entrée de journal (offline-first) pointant vers une entité et sa révision locale.

    ``is_pending`` passe à ``False`` après accusé de réception logique côté couche sync
    (sans transport implémenté dans ce package).

    :ivar mutation_id: Identifiant stable de l'entrée de journal.
    :ivar entity_kind: Type d'entité métier concernée.
    :ivar entity_id: Identifiant de l'entité modifiée.
    :ivar kind: Nature de la mutation fonctionnelle.
    :ivar recorded_at: Horodatage d'enregistrement local (idéalement timezone-aware).
    :ivar entity_version_at_record: Valeur de :class:`EntityVersion` au moment du journal.
    :ivar sync_state_at_record: :class:`SyncState` de l'entité au moment du journal.
    :ivar payload_hints: Paires clé/valeur sérialisables (indices pour la future couche sync).
    :ivar is_pending: Vrai tant que la mutation n'a pas été acquittée localement post-push.
    """

    mutation_id: DomainId
    entity_kind: LocalEntityKind
    entity_id: DomainId
    kind: LocalMutationKind
    recorded_at: datetime
    entity_version_at_record: int
    sync_state_at_record: SyncState
    payload_hints: tuple[tuple[str, str], ...] = ()
    is_pending: bool = True

    def with_acknowledged(self) -> LocalMutation:
        """Copie identique avec ``is_pending=False`` (succès de synchro côté orchestration)."""
        return replace(self, is_pending=False)

    def to_serializable(self) -> dict[str, object]:
        """Représentation JSON-friendly pour export ou debug."""
        return {
            "mutation_id": self.mutation_id.value,
            "entity_kind": self.entity_kind.value,
            "entity_id": self.entity_id.value,
            "kind": self.kind.value,
            "recorded_at": self.recorded_at.isoformat(),
            "entity_version_at_record": self.entity_version_at_record,
            "sync_state_at_record": self.sync_state_at_record.value,
            "payload_hints": dict(self.payload_hints),
            "is_pending": self.is_pending,
        }
