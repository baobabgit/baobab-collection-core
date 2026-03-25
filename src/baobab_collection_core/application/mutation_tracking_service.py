"""API applicative : journal offline-first des mutations et transitions de synchro."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.local_mutation import LocalMutation
from baobab_collection_core.domain.local_mutation_kind import LocalMutationKind
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.invalid_local_mutation_exception import (
    InvalidLocalMutationException,
)
from baobab_collection_core.exceptions.mutation_not_found_exception import MutationNotFoundException
from baobab_collection_core.ports.local_mutation_journal_port import LocalMutationJournalPort

_MAX_PAYLOAD_ENTRIES = 32
_MAX_PAYLOAD_KEY_LEN = 64
_MAX_PAYLOAD_VALUE_LEN = 512


class MutationTrackingService:
    """Enregistre les mutations locales et permet d'extraire les changements en attente.

    Ce service **ne remplace pas** les règles métier des agrégats : les entités doivent
    toujours passer par leurs méthodes (``bump_version``, ``mark_deleted``, etc.).
    Le journal complète la traçabilité pour une couche de synchronisation future.

    :param journal: Port du journal local injecté.
    """

    __slots__ = ("_journal",)

    def __init__(self, journal: LocalMutationJournalPort) -> None:
        self._journal = journal

    def record_local_mutation(
        self,
        *,
        entity_kind: LocalEntityKind,
        entity_id: DomainId,
        kind: LocalMutationKind,
        recorded_at: datetime,
        entity_version_at_record: int,
        sync_state_at_record: SyncState,
        payload_hints: Sequence[tuple[str, str]] | None = None,
        mutation_id: DomainId | None = None,
    ) -> LocalMutation:
        """Enregistre une mutation **pending** dans le journal.

        :param mutation_id: Identifiant imposé (tests) ou ``None`` pour allocation UUID.
        :raises InvalidLocalMutationException: si les paramètres sont incohérents.
        """
        if entity_version_at_record < 0:
            raise InvalidLocalMutationException(
                "La version d'entité associée à une mutation ne peut pas être négative."
            )
        hints = MutationTrackingService._normalize_payload(payload_hints)
        mid = mutation_id if mutation_id is not None else DomainId(str(uuid.uuid4()))
        if self._journal.get_by_id(mid) is not None:
            raise InvalidLocalMutationException(
                "Une mutation portant cet identifiant existe déjà dans le journal."
            )
        entry = LocalMutation(
            mutation_id=mid,
            entity_kind=entity_kind,
            entity_id=entity_id,
            kind=kind,
            recorded_at=recorded_at,
            entity_version_at_record=entity_version_at_record,
            sync_state_at_record=sync_state_at_record,
            payload_hints=hints,
            is_pending=True,
        )
        self._journal.append(entry)
        return entry

    def record_from_entity_snapshot(
        self,
        *,
        entity_kind: LocalEntityKind,
        entity_id: DomainId,
        kind: LocalMutationKind,
        metadata: EntityMetadata,
        recorded_at: datetime,
        payload_hints: Sequence[tuple[str, str]] | None = None,
        mutation_id: DomainId | None = None,
    ) -> LocalMutation:
        """Enregistre une mutation à partir d'un instantané cohérent de :class:`EntityMetadata`."""
        return self.record_local_mutation(
            entity_kind=entity_kind,
            entity_id=entity_id,
            kind=kind,
            recorded_at=recorded_at,
            entity_version_at_record=metadata.version.value,
            sync_state_at_record=metadata.sync_state,
            payload_hints=payload_hints,
            mutation_id=mutation_id,
        )

    def list_pending_mutations(self) -> tuple[LocalMutation, ...]:
        """Retourne les mutations encore en attente (triées pour stabilité d'UI / batch)."""
        pending = [m for m in self._journal.list_pending() if m.is_pending]
        pending.sort(key=lambda m: (m.recorded_at, m.mutation_id.value))
        return tuple(pending)

    def extract_pending_changes(self) -> tuple[LocalMutation, ...]:
        """Alias explicite pour l'extraction des changements non synchronisés."""
        return self.list_pending_mutations()

    def acknowledge_mutations(self, mutation_ids: Sequence[DomainId]) -> None:
        """Marque des mutations comme acquittées après succès de push (orchestration future).

        :raises MutationNotFoundException: si une entrée est absente.
        :raises InvalidLocalMutationException: si une entrée n'était plus pending.
        """
        for mid in mutation_ids:
            current = self._journal.get_by_id(mid)
            if current is None:
                raise MutationNotFoundException(
                    "Aucune mutation ne correspond à l'identifiant fourni pour l'acquittement."
                )
            if not current.is_pending:
                raise InvalidLocalMutationException(
                    "La mutation ne peut pas être acquittée car elle n'est plus en attente."
                )
            self._journal.replace(current.with_acknowledged())

    def acknowledge_all_pending_for_entity(self, entity_id: DomainId) -> int:
        """Acquitte toutes les mutations pending pour ``entity_id`` ; retourne le nombre traité."""
        to_ack = [
            m.mutation_id
            for m in self.list_pending_mutations()
            if m.entity_id.value == entity_id.value
        ]
        self.acknowledge_mutations(to_ack)
        return len(to_ack)

    def pending_mutation_count(self) -> int:
        """Nombre de mutations encore en attente."""
        return len(self.list_pending_mutations())

    @staticmethod
    def suggested_metadata_after_successful_push(
        metadata: EntityMetadata,
        moment: datetime,
    ) -> EntityMetadata:
        """Proposition de métadonnées « alignées serveur » sans transport (état ``SYNCED``).

        À appliquer sur l'entité **après** accusé de synchro distant ; ne modifie pas la version.
        """
        return metadata.touch(moment, sync_state=SyncState.SYNCED)

    @staticmethod
    def suggested_metadata_mark_conflict(
        metadata: EntityMetadata, moment: datetime
    ) -> EntityMetadata:
        """Marque un état de divergence locale exploitable par une future résolution."""
        return metadata.touch(moment, sync_state=SyncState.CONFLICT)

    @staticmethod
    def _normalize_payload(raw: Sequence[tuple[str, str]] | None) -> tuple[tuple[str, str], ...]:
        if raw is None:
            return ()
        if len(raw) > _MAX_PAYLOAD_ENTRIES:
            raise InvalidLocalMutationException(
                f"Le journal accepte au plus {_MAX_PAYLOAD_ENTRIES} entrées de payload."
            )
        out: list[tuple[str, str]] = []
        for key, value in raw:
            k = key.strip()
            v = value.strip()
            if not k:
                raise InvalidLocalMutationException("Une clé de payload ne peut pas être vide.")
            if len(k) > _MAX_PAYLOAD_KEY_LEN or len(v) > _MAX_PAYLOAD_VALUE_LEN:
                raise InvalidLocalMutationException(
                    "Clé ou valeur de payload dépasse la taille maximale autorisée."
                )
            out.append((k, v))
        return tuple(out)
