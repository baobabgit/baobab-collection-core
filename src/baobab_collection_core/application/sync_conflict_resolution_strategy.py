"""Stratégies injectables de résolution de conflit (sans infrastructure)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from baobab_collection_core.domain.conflict_resolution_decision import ConflictResolutionDecision
from baobab_collection_core.domain.sync_conflict import SyncConflict
from baobab_collection_core.domain.sync_dtos import (
    LocalEntitySyncSnapshot,
    RemoteEntitySyncSnapshot,
)
from baobab_collection_core.domain.sync_session_outcome import SyncSessionOutcome
from baobab_collection_core.exceptions.invalid_sync_conflict_resolution_exception import (
    InvalidSyncConflictResolutionException,
)


@runtime_checkable
class SyncConflictResolutionStrategy(Protocol):
    """Contrat pour brancher des politiques métier ou des modules de fusion futurs."""

    def resolve(
        self,
        conflict: SyncConflict,
        *,
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> ConflictResolutionDecision:
        """Produit une décision déterministe ou explicitement manuelle."""


class LocalWinsSyncConflictStrategy:
    """Priorise systématiquement l'état local (push / réécriture distante attendue)."""

    __slots__ = ()

    def resolve(
        self,
        conflict: SyncConflict,
        *,
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> ConflictResolutionDecision:
        """Garde la branche locale comme source de vérité adoptée."""
        return ConflictResolutionDecision(
            outcome=SyncSessionOutcome.SYNCED,
            winner="local",
            adopted_version=local.version,
            adopted_parent_container_id=local.parent_container_id,
            requires_manual_resolution=False,
            notes=(
                "Application de la politique « local prioritaire » "
                f"({conflict.kind.value}, distant_présent={remote.present})."
            ),
        )


class RemoteWinsSyncConflictStrategy:
    """Aligne le client sur l'état distant (y compris tombes et parents distants)."""

    __slots__ = ()

    def resolve(
        self,
        conflict: SyncConflict,
        *,
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> ConflictResolutionDecision:
        """Adopte révision, parent et tombe distants lorsque c'est possible."""
        if not remote.present:
            raise InvalidSyncConflictResolutionException(
                "La stratégie « distant prioritaire » exige un instantané distant présent."
            )
        parent = None if remote.is_logically_deleted else remote.parent_container_id
        return ConflictResolutionDecision(
            outcome=SyncSessionOutcome.SYNCED,
            winner="remote",
            adopted_version=remote.version,
            adopted_parent_container_id=parent,
            requires_manual_resolution=False,
            notes=(
                "Application de la politique « distant prioritaire » "
                f"({conflict.kind.value}, client v{local.version})."
            ),
        )


class ExplicitManualSyncConflictStrategy:
    """Ne tranche pas : explicite un conflit à traiter hors automate."""

    __slots__ = ()

    def resolve(
        self,
        conflict: SyncConflict,
        *,
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> ConflictResolutionDecision:
        """Refuse le compromis automatique : issue CONFLICT explicite."""
        return ConflictResolutionDecision(
            outcome=SyncSessionOutcome.CONFLICT,
            winner="manual",
            adopted_version=None,
            adopted_parent_container_id=None,
            requires_manual_resolution=True,
            notes=(
                f"Intervention requise ({conflict.kind.value}, "
                f"client v{local.version}, distant_présent={remote.present})."
            ),
        )
