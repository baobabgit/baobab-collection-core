"""Classification fine des conflits de synchronisation local / distant."""

from enum import StrEnum


class SyncConflictKind(StrEnum):
    """Type métier de divergence nécessitant une décision explicite.

    :cvar CONCURRENT_MODIFICATION: Même révision apparente mais empreintes divergentes.
    :cvar REMOTE_DELETED_LOCAL_MODIFIED: Tombeau distant alors que le client a du travail local.
    :cvar VERSION_DIVERGENCE: Numéros de version différents avec travail local en attente.
    :cvar CONCURRENT_PARENT_CHANGE: Parent / contenant différent du côté pair.
    :cvar LOGICAL_EXTERNAL_ID_COLLISION: Clés métier externes incohérentes pour la même entité.
    """

    CONCURRENT_MODIFICATION = "concurrent_modification"
    REMOTE_DELETED_LOCAL_MODIFIED = "remote_deleted_local_modified"
    VERSION_DIVERGENCE = "version_divergence"
    CONCURRENT_PARENT_CHANGE = "concurrent_parent_change"
    LOGICAL_EXTERNAL_ID_COLLISION = "logical_external_id_collision"
