"""Instantanés et structures de passage pour le cœur de synchronisation."""

from __future__ import annotations

from dataclasses import dataclass

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.sync_delta_kind import SyncDeltaKind
from baobab_collection_core.domain.sync_plan_action import SyncPlanAction
from baobab_collection_core.domain.sync_session_outcome import SyncSessionOutcome
from baobab_collection_core.domain.sync_state import SyncState


@dataclass(frozen=True, slots=True)
class LocalEntitySyncSnapshot:  # pylint: disable=too-many-instance-attributes
    """Vue locale minimaliste pour la couche de synchro (sans entité complète).

    :ivar entity_id: Identifiant de l'entité.
    :ivar entity_kind: Type métier stable.
    :ivar version: Révision locale (entier, sémantique alignée sur ``EntityVersion`` du domaine).
    :ivar sync_state: État dans le pipeline local.
    :ivar is_logically_deleted: Tombeau logique observé localement.
    :ivar parent_container_id: Contenant parent courant, si la modélisation le permet.
    :ivar content_fingerprint: Empreinte optionnelle pour détecter des forks de contenu.
    :ivar external_business_key: Clé métier externe (SKU, codes catalogue, etc.).
    """

    entity_id: DomainId
    entity_kind: LocalEntityKind
    version: int
    sync_state: SyncState
    is_logically_deleted: bool
    parent_container_id: DomainId | None = None
    content_fingerprint: str | None = None
    external_business_key: str | None = None

    def has_unresolved_local_work(self) -> bool:
        """Vrai si des changements locaux ou erreurs requièrent encore une action de synchro."""
        return self.sync_state in (
            SyncState.DIRTY,
            SyncState.DELETED,
            SyncState.CONFLICT,
            SyncState.SYNC_ERROR,
        )


@dataclass(frozen=True, slots=True)
class RemoteEntitySyncSnapshot:  # pylint: disable=too-many-instance-attributes
    """État connu ou supposé côté pair (fourni par un futur adaptateur).

    :ivar entity_id: Identifiant corrélé localement.
    :ivar present: Faux si l'entité n'existe pas encore distamment.
    :ivar version: Révision distante ; ignorée si ``present`` est faux.
    :ivar is_logically_deleted: Tombeau côté pair.
    :ivar parent_container_id: Contenant parent côté pair (optionnel).
    :ivar content_fingerprint: Empreinte de contenu distante (optionnel).
    :ivar external_business_key: Clé métier externe distante (optionnel).
    """

    entity_id: DomainId
    present: bool
    version: int
    is_logically_deleted: bool
    parent_container_id: DomainId | None = None
    content_fingerprint: str | None = None
    external_business_key: str | None = None


@dataclass(frozen=True, slots=True)
class EntitySyncDelta:
    """Écart calculé pour une paire local / distant."""

    entity_id: DomainId
    entity_kind: LocalEntityKind
    kind: SyncDeltaKind
    local_version: int
    remote_version: int | None
    remote_present: bool


@dataclass(frozen=True, slots=True)
class SyncPlanItem:
    """Une opération ordonnée dans un plan."""

    entity_id: DomainId
    entity_kind: LocalEntityKind
    action: SyncPlanAction
    source_delta: SyncDeltaKind


@dataclass(frozen=True, slots=True)
class SyncPlan:
    """Plan agrégé ; ``plan_id`` est un libellé libre (ex. UUID côté orchestrateur)."""

    plan_id: str
    items: tuple[SyncPlanItem, ...]


@dataclass(frozen=True, slots=True)
class EntitySyncApplyRecord:
    """Résultat appliqué (ou attendu) pour une entité dans un batch."""

    entity_id: DomainId
    outcome: SyncSessionOutcome
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class SynchronizationBatchResult:
    """Résultat de session après application ou simulation."""

    session_outcome: SyncSessionOutcome
    records: tuple[EntitySyncApplyRecord, ...]
