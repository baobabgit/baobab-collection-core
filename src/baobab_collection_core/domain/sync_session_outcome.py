"""Résultat agrégé ou par entité pour une session de synchronisation."""

from enum import StrEnum


class SyncSessionOutcome(StrEnum):
    """Statut fonctionnel demandé pour le cœur de synchro (sans transport).

    Orthogonal aux :class:`~baobab_collection_core.domain.sync_state.SyncState` par entité
    mais mappable (ex. ``SYNCED`` ↔ ``SyncState.SYNCED``).

    :cvar SYNCED: Session ou entité alignée avec le pair distant.
    :cvar PENDING: Travail encore à poursuivre (push/pull à exécuter ou en cours).
    :cvar CONFLICT: Divergence nécessitant une résolution (hors périmètre ici).
    :cvar SYNC_ERROR: Échec retentable côté orchestration ou transport futur.
    """

    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"
    SYNC_ERROR = "sync_error"
