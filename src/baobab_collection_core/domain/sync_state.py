"""États transverses du cycle de synchronisation offline-first."""

from enum import StrEnum


class SyncState(StrEnum):
    """Indique où en est l'objet dans le pipeline de synchronisation.

    Les valeurs sont des chaînes stables pour faciliter la persistance et les API.

    :cvar CLEAN: Aucune mutation locale en attente de propagation.
    :cvar DIRTY: Des changements locaux ne sont pas encore poussés.
    :cvar SYNCED: Dernière synchronisation réussie avec le serveur.
    :cvar CONFLICT: Divergence détectée avec le serveur ou un pair.
    :cvar SYNC_ERROR: Dernière tentative de sync a échoué de manière retentable.
    :cvar DELETED: Suppression logique connue côté client (à propager).
    """

    CLEAN = "clean"
    DIRTY = "dirty"
    SYNCED = "synced"
    CONFLICT = "conflict"
    SYNC_ERROR = "sync_error"
    DELETED = "deleted"
