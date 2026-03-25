"""Cas d'usage applicatifs pour les exemplaires physiques."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.collection_card import UNSET
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.physical_copy import PhysicalCopy
from baobab_collection_core.domain.physical_copy_business_status import PhysicalCopyBusinessStatus
from baobab_collection_core.domain.physical_copy_condition import PhysicalCopyCondition
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.physical_copy_not_found_exception import (
    PhysicalCopyNotFoundException,
)
from baobab_collection_core.ports.physical_copy_repository_port import PhysicalCopyRepositoryPort


class PhysicalCopyApplicationService:
    """Orchestration CRUD + transitions d'état sur :class:`PhysicalCopy`.

    :param copies: Port de persistance injecté.
    """

    __slots__ = ("_copies",)

    def __init__(self, copies: PhysicalCopyRepositoryPort) -> None:
        self._copies = copies

    def create_copy(  # pylint: disable=too-many-arguments
        self,
        card_id: DomainId,
        owner_user_id: DomainId,
        moment: datetime,
        *,
        physical_condition: PhysicalCopyCondition,
        business_status: PhysicalCopyBusinessStatus,
        container_id: DomainId | None = None,
        location_note: str | None = None,
        language: str | None = None,
        finish: str | None = None,
        notes: str | None = None,
    ) -> PhysicalCopy:
        """Crée un exemplaire rattaché à une carte et un propriétaire."""
        entity_id = DomainId(str(uuid.uuid4()))
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.DIRTY,
        )
        physical_copy = PhysicalCopy.create(
            entity_id,
            card_id,
            owner_user_id,
            metadata,
            physical_condition=physical_condition,
            business_status=business_status,
            container_id=container_id,
            location_note=location_note,
            language=language,
            finish=finish,
            notes=notes,
        )
        self._copies.save(physical_copy)
        return physical_copy

    def update_copy_details(
        self,
        copy_id: DomainId,
        moment: datetime,
        *,
        location_note: str | None | Any = UNSET,
        language: str | None | Any = UNSET,
        finish: str | None | Any = UNSET,
        notes: str | None | Any = UNSET,
    ) -> PhysicalCopy:
        """Actualise les champs descriptifs optionnels."""
        physical_copy = self._require_active_copy(copy_id)
        physical_copy.update_details(
            moment,
            location_note=location_note,
            language=language,
            finish=finish,
            notes=notes,
        )
        self._copies.save(physical_copy)
        return physical_copy

    def change_physical_condition(
        self,
        copy_id: DomainId,
        moment: datetime,
        condition: PhysicalCopyCondition,
    ) -> PhysicalCopy:
        """Met à jour l'état matériel."""
        physical_copy = self._require_active_copy(copy_id)
        physical_copy.change_physical_condition(moment, condition)
        self._copies.save(physical_copy)
        return physical_copy

    def change_business_status(
        self,
        copy_id: DomainId,
        moment: datetime,
        status: PhysicalCopyBusinessStatus,
    ) -> PhysicalCopy:
        """Met à jour le statut métier."""
        physical_copy = self._require_active_copy(copy_id)
        physical_copy.change_business_status(moment, status)
        self._copies.save(physical_copy)
        return physical_copy

    def attach_container(
        self,
        copy_id: DomainId,
        moment: datetime,
        container_id: DomainId,
    ) -> PhysicalCopy:
        """Rattache la copie à un contenant en remplaçant l'association précédente."""
        physical_copy = self._require_active_copy(copy_id)
        physical_copy.attach_to_container(moment, container_id)
        self._copies.save(physical_copy)
        return physical_copy

    def detach_container(self, copy_id: DomainId, moment: datetime) -> PhysicalCopy:
        """Supprime le rattachement à un contenant."""
        physical_copy = self._require_active_copy(copy_id)
        physical_copy.detach_from_container(moment)
        self._copies.save(physical_copy)
        return physical_copy

    def soft_delete_copy(self, copy_id: DomainId, moment: datetime) -> PhysicalCopy:
        """Applique une suppression logique (fin de vie synchronisable)."""
        physical_copy = self._require_active_copy(copy_id)
        physical_copy.soft_delete(moment)
        self._copies.save(physical_copy)
        return physical_copy

    def get_copy_by_id(self, copy_id: DomainId) -> PhysicalCopy:
        """Retourne une copie active ou lève :class:`PhysicalCopyNotFoundException`."""
        return self._require_active_copy(copy_id)

    def list_copies_for_card(self, card_id: DomainId) -> list[PhysicalCopy]:
        """Liste les exemplaires actifs liés à une carte."""
        return [
            copy for copy in self._copies.list_by_card_id(card_id) if not copy.is_logically_deleted
        ]

    def _require_active_copy(self, copy_id: DomainId) -> PhysicalCopy:
        physical_copy = self._copies.get_by_id(copy_id)
        if physical_copy is None or physical_copy.is_logically_deleted:
            raise PhysicalCopyNotFoundException(
                "Aucune copie active ne correspond à l'identifiant fourni dans la collection."
            )
        return physical_copy
