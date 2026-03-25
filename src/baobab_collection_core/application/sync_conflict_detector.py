"""Détection déterministe de conflits à partir d'instantanés local / distant."""

from __future__ import annotations

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.sync_conflict import SyncConflict
from baobab_collection_core.domain.sync_conflict_kind import SyncConflictKind
from baobab_collection_core.domain.sync_dtos import (
    LocalEntitySyncSnapshot,
    RemoteEntitySyncSnapshot,
)
from baobab_collection_core.exceptions.invalid_sync_snapshot_exception import (
    InvalidSyncSnapshotException,
)


def _same_parent(
    local: DomainId | None,
    remote: DomainId | None,
) -> bool:
    if local is None and remote is None:
        return True
    if local is None or remote is None:
        return False
    return local.value == remote.value


class SyncConflictDetector:
    """Inspecte une paire d'instantanés et retourne au plus un conflit typé.

    L'ordre d'évaluation privilégie les collisions explicites puis les tombes distantes,
    les divergences de parent, les forks de contenu à révision égale, puis les versions.
    """

    __slots__ = ()

    def detect(
        self,
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> SyncConflict | None:
        """Retourne un conflit métier ou ``None`` si aucune divergence n'est détectée ici."""
        SyncConflictDetector._validate_pair(local, remote)

        if conflict := SyncConflictDetector._detect_logical_external_id_collision(local, remote):
            return conflict
        if conflict := SyncConflictDetector._detect_remote_deleted_local_dirty(local, remote):
            return conflict
        if conflict := SyncConflictDetector._detect_concurrent_parent(local, remote):
            return conflict
        if conflict := SyncConflictDetector._detect_concurrent_modification(local, remote):
            return conflict
        if conflict := SyncConflictDetector._detect_version_divergence(local, remote):
            return conflict
        return None

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
    def _remote_row_ready(remote: RemoteEntitySyncSnapshot) -> bool:
        return remote.present and not remote.is_logically_deleted

    @staticmethod
    def _detect_logical_external_id_collision(
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> SyncConflict | None:
        if not remote.present:
            return None
        lk = local.external_business_key
        rk = remote.external_business_key
        if lk is None or rk is None:
            return None
        if lk.strip() == rk.strip():
            return None
        return SyncConflict(
            entity_id=local.entity_id,
            entity_kind=local.entity_kind,
            kind=SyncConflictKind.LOGICAL_EXTERNAL_ID_COLLISION,
            summary="Clés métier externes divergentes pour la même entité.",
            local_version=local.version,
            remote_version=remote.version,
        )

    @staticmethod
    def _detect_remote_deleted_local_dirty(
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> SyncConflict | None:
        if not (remote.present and remote.is_logically_deleted):
            return None
        if not local.has_unresolved_local_work():
            return None
        if local.is_logically_deleted:
            return None
        return SyncConflict(
            entity_id=local.entity_id,
            entity_kind=local.entity_kind,
            kind=SyncConflictKind.REMOTE_DELETED_LOCAL_MODIFIED,
            summary=(
                "Tombeau distant alors que des changements locaux "
                "sont encore en attente de propagation."
            ),
            local_version=local.version,
            remote_version=remote.version,
        )

    @staticmethod
    def _detect_concurrent_parent(
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> SyncConflict | None:
        if not SyncConflictDetector._remote_row_ready(remote):
            return None
        if local.is_logically_deleted:
            return None
        if _same_parent(local.parent_container_id, remote.parent_container_id):
            return None
        if not local.has_unresolved_local_work():
            return None
        return SyncConflict(
            entity_id=local.entity_id,
            entity_kind=local.entity_kind,
            kind=SyncConflictKind.CONCURRENT_PARENT_CHANGE,
            summary=(
                "Contenant parent différent côté client et serveur "
                "avec travail local en attente."
            ),
            local_version=local.version,
            remote_version=remote.version,
        )

    @staticmethod
    def _detect_concurrent_modification(  # pylint: disable=too-many-return-statements
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> SyncConflict | None:
        if not SyncConflictDetector._remote_row_ready(remote):
            return None
        if local.is_logically_deleted:
            return None
        if not local.has_unresolved_local_work():
            return None
        if local.version != remote.version:
            return None
        lf = local.content_fingerprint
        rf = remote.content_fingerprint
        if lf is None or rf is None:
            return None
        if lf == rf:
            return None
        return SyncConflict(
            entity_id=local.entity_id,
            entity_kind=local.entity_kind,
            kind=SyncConflictKind.CONCURRENT_MODIFICATION,
            summary="Révision identique mais empreintes de contenu divergentes.",
            local_version=local.version,
            remote_version=remote.version,
        )

    @staticmethod
    def _detect_version_divergence(
        local: LocalEntitySyncSnapshot,
        remote: RemoteEntitySyncSnapshot,
    ) -> SyncConflict | None:
        if not SyncConflictDetector._remote_row_ready(remote):
            return None
        if local.is_logically_deleted:
            return None
        if not local.has_unresolved_local_work():
            return None
        if local.version == remote.version:
            return None
        return SyncConflict(
            entity_id=local.entity_id,
            entity_kind=local.entity_kind,
            kind=SyncConflictKind.VERSION_DIVERGENCE,
            summary="Révisions locales et distantes divergent avec travail client en attente.",
            local_version=local.version,
            remote_version=remote.version,
        )
