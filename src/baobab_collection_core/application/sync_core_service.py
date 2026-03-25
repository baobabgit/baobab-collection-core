"""Cœur applicatif de synchronisation : comparaison, plan et mise à jour de métadonnées."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.sync_delta_kind import SyncDeltaKind
from baobab_collection_core.domain.sync_dtos import (
    EntitySyncApplyRecord,
    EntitySyncDelta,
    LocalEntitySyncSnapshot,
    RemoteEntitySyncSnapshot,
    SyncPlan,
    SyncPlanItem,
    SynchronizationBatchResult,
)
from baobab_collection_core.domain.sync_plan_action import SyncPlanAction
from baobab_collection_core.domain.sync_session_outcome import SyncSessionOutcome
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.invalid_sync_snapshot_exception import (
    InvalidSyncSnapshotException,
)
from baobab_collection_core.ports.remote_entity_sync_snapshot_port import (
    RemoteEntitySyncSnapshotPort,
)


class SyncCoreService:
    """Compare local / distant, produit un plan et met à jour des :class:`EntityMetadata`.

    Sans transport : le port distant ne fournit qu'un
    :class:`~baobab_collection_core.domain.sync_dtos.RemoteEntitySyncSnapshot` (tests, adaptateurs).
    """

    __slots__ = ("_remote",)

    def __init__(self, remote: RemoteEntitySyncSnapshotPort | None = None) -> None:
        self._remote = remote

    def compare(
        self,
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> EntitySyncDelta:
        """Calcule l'écart entre instantanés cohérents (même ``entity_id``)."""
        SyncCoreService._validate_pair(local, remote)
        kind = SyncCoreService._resolve_delta_kind(local, remote)
        remote_ver = remote.version if remote.present else None
        return EntitySyncDelta(
            entity_id=local.entity_id,
            entity_kind=local.entity_kind,
            kind=kind,
            local_version=local.version,
            remote_version=remote_ver,
            remote_present=remote.present,
        )

    def fetch_and_compare(self, local: LocalEntitySyncSnapshot) -> EntitySyncDelta:
        """Combine récupération via port distant et comparaison.

        :raises InvalidSyncSnapshotException: si aucun port distant n'est configuré.
        """
        if self._remote is None:
            raise InvalidSyncSnapshotException(
                "Aucun port distant n'est disponible pour fetch_and_compare."
            )
        remote = self._remote.fetch_snapshot(local.entity_id, local.entity_kind)
        return self.compare(local, remote)

    def build_plan(
        self, deltas: tuple[EntitySyncDelta, ...], *, plan_id: str | None = None
    ) -> SyncPlan:
        """Projette des écarts en actions ordonnées."""
        pid = plan_id if plan_id is not None else str(uuid4())
        items = tuple(
            SyncPlanItem(
                entity_id=d.entity_id,
                entity_kind=d.entity_kind,
                action=SyncCoreService._action_for_delta(d.kind),
                source_delta=d.kind,
            )
            for d in sorted(deltas, key=lambda x: (x.entity_kind.value, x.entity_id.value))
        )
        return SyncPlan(plan_id=pid, items=items)

    @staticmethod
    def consolidate_session_outcome(
        records: tuple[EntitySyncApplyRecord, ...],
    ) -> SyncSessionOutcome:
        """Agrège les issues avec priorité conflit > erreur > attente > succès."""
        outcomes = {r.outcome for r in records}
        if SyncSessionOutcome.CONFLICT in outcomes:
            return SyncSessionOutcome.CONFLICT
        if SyncSessionOutcome.SYNC_ERROR in outcomes:
            return SyncSessionOutcome.SYNC_ERROR
        if SyncSessionOutcome.PENDING in outcomes:
            return SyncSessionOutcome.PENDING
        return SyncSessionOutcome.SYNCED

    def build_batch_result(
        self, records: tuple[EntitySyncApplyRecord, ...]
    ) -> SynchronizationBatchResult:
        """Emboîte les enregistrements avec un statut de session consolidé."""
        return SynchronizationBatchResult(
            session_outcome=SyncCoreService.consolidate_session_outcome(records),
            records=records,
        )

    @staticmethod
    def apply_entity_outcome_to_metadata(
        metadata: EntityMetadata,
        outcome: SyncSessionOutcome,
        moment: datetime,
        *,
        confirmed_remote_version: int | None = None,
    ) -> EntityMetadata:
        """Met à jour les métadonnées en fonction du résultat applicatif pour une entité.

        :param confirmed_remote_version: Si ``outcome`` est ``SYNCED``, version confirmée distante.
        """
        if outcome is SyncSessionOutcome.SYNCED:
            if confirmed_remote_version is not None:
                if confirmed_remote_version < metadata.version.value:
                    raise InvalidSyncSnapshotException(
                        "La version distante confirmée ne peut pas être strictement "
                        "inférieure à la version locale."
                    )
                new_ts = metadata.timestamps.with_updated_at(moment)
                new_meta = replace(
                    metadata,
                    timestamps=new_ts,
                    version=EntityVersion(confirmed_remote_version),
                    sync_state=SyncState.SYNCED,
                )
                new_meta.require_monotone_version(metadata.version)
                return new_meta
            return metadata.touch(moment, sync_state=SyncState.SYNCED)
        if outcome is SyncSessionOutcome.CONFLICT:
            return metadata.touch(moment, sync_state=SyncState.CONFLICT)
        if outcome is SyncSessionOutcome.SYNC_ERROR:
            return metadata.touch(moment, sync_state=SyncState.SYNC_ERROR)
        if outcome is SyncSessionOutcome.PENDING:
            return metadata.touch(moment, sync_state=SyncState.DIRTY)
        raise InvalidSyncSnapshotException(
            "Résultat de synchro inconnu pour application sur métadonnées."
        )

    @staticmethod
    def _validate_pair(local: LocalEntitySyncSnapshot, remote: RemoteEntitySyncSnapshot) -> None:
        if local.entity_id.value != remote.entity_id.value:
            raise InvalidSyncSnapshotException(
                "Les instantanés local et distant doivent partager le même entity_id."
            )
        if local.version < 0:
            raise InvalidSyncSnapshotException("La version locale ne peut pas être négative.")
        if remote.present and remote.version < 0:
            raise InvalidSyncSnapshotException(
                "La version distante ne peut pas être négative si l'entité existe."
            )

    @staticmethod
    def _resolve_delta_kind(  # pylint: disable=too-many-return-statements
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> SyncDeltaKind:
        unresolved = local.has_unresolved_local_work()

        if local.is_logically_deleted and remote.is_logically_deleted:
            return SyncDeltaKind.NONE
        if local.is_logically_deleted and not remote.is_logically_deleted and remote.present:
            return SyncDeltaKind.PUSH
        if not local.is_logically_deleted and remote.is_logically_deleted and remote.present:
            return SyncDeltaKind.PULL

        if not remote.present:
            return SyncDeltaKind.PUSH if unresolved else SyncDeltaKind.NONE

        if local.version < remote.version and unresolved:
            return SyncDeltaKind.CONFLICT
        if local.version < remote.version and not unresolved:
            return SyncDeltaKind.PULL
        if local.version > remote.version:
            return SyncDeltaKind.PUSH
        if local.version == remote.version:
            return SyncDeltaKind.PUSH if unresolved else SyncDeltaKind.NONE
        return SyncDeltaKind.NONE

    @staticmethod
    def _action_for_delta(kind: SyncDeltaKind) -> SyncPlanAction:
        if kind is SyncDeltaKind.NONE:
            return SyncPlanAction.NO_OP
        if kind is SyncDeltaKind.PUSH:
            return SyncPlanAction.PUSH
        if kind is SyncDeltaKind.PULL:
            return SyncPlanAction.PULL
        return SyncPlanAction.REPORT_CONFLICT
