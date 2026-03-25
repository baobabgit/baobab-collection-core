"""Exemplaire physique d'une carte de collection."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from baobab_collection_core.domain.collection_card import UNSET
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_base import EntityBase
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.physical_copy_business_status import PhysicalCopyBusinessStatus
from baobab_collection_core.domain.physical_copy_condition import PhysicalCopyCondition
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.invalid_physical_copy_exception import (
    InvalidPhysicalCopyException,
)

_MAX_LOCATION_LEN = 512
_MAX_LANGUAGE_LEN = 32
_MAX_FINISH_LEN = 128
_MAX_NOTES_LEN = 4000


class PhysicalCopy(EntityBase):  # pylint: disable=too-many-instance-attributes
    """Exemplaire concret rattaché à une carte de collection (:class:`CollectionCard`).

    Distinct de la référence carte : plusieurs copies peuvent partager le même ``card_id``.
    Le ``entity_id`` de cette entité identifie l'exemplaire dans la synchronisation future.

    :param entity_id: Identifiant interne de la copie.
    :param card_id: Référence stable vers la carte possédée.
    :param owner_user_id: Propriétaire (usager) responsable de l'exemplaire.
    :param metadata: Audit, version optimiste et synchro.
    :param physical_condition: État matériel courant.
    :param business_status: Statut métier courant.
    :param container_id: Contenant optionnel (boîte, classeur, etc.).
    :param location_note: Libellé libre d'emplacement physique optionnel.
    :param language: Langue optionnelle (ex. version linguistique de la carte).
    :param finish: Finition optionnelle (holo, reverse…).
    :param notes: Notes privées optionnelles.

    :ivar _card_id: Référence carte immuable après création.
    :ivar _owner_user_id: Propriétaire immuable après création.
    :ivar _container_id: Contenant courant (au plus un).
    :ivar _location_note: Emplacement optionnel.
    :ivar _physical_condition: État matériel.
    :ivar _business_status: Statut métier.
    :ivar _language: Langue optionnelle.
    :ivar _finish: Finition optionnelle.
    :ivar _notes: Notes libres.
    """

    __slots__ = (
        "_card_id",
        "_owner_user_id",
        "_container_id",
        "_location_note",
        "_physical_condition",
        "_business_status",
        "_language",
        "_finish",
        "_notes",
    )

    def __init__(  # pylint: disable=too-many-arguments
        self,
        entity_id: DomainId,
        card_id: DomainId,
        owner_user_id: DomainId,
        metadata: EntityMetadata,
        *,
        physical_condition: PhysicalCopyCondition,
        business_status: PhysicalCopyBusinessStatus,
        container_id: DomainId | None = None,
        location_note: str | None = None,
        language: str | None = None,
        finish: str | None = None,
        notes: str | None = None,
    ) -> None:
        super().__init__(entity_id, metadata)
        self._card_id = card_id
        self._owner_user_id = owner_user_id
        self._physical_condition = physical_condition
        self._business_status = business_status
        self._container_id = container_id
        self._location_note = PhysicalCopy._optional_text(
            location_note, "location_note", _MAX_LOCATION_LEN
        )
        self._language = PhysicalCopy._optional_text(language, "language", _MAX_LANGUAGE_LEN)
        self._finish = PhysicalCopy._optional_text(finish, "finish", _MAX_FINISH_LEN)
        self._notes = PhysicalCopy._optional_text(notes, "notes", _MAX_NOTES_LEN)

    @property
    def card_id(self) -> DomainId:
        """Carte de référence pour cet exemplaire."""
        return self._card_id

    @property
    def owner_user_id(self) -> DomainId:
        """Propriétaire courant."""
        return self._owner_user_id

    @property
    def container_id(self) -> DomainId | None:
        """Contenant actuel, s'il existe."""
        return self._container_id

    @property
    def location_note(self) -> str | None:
        """Description libre d'emplacement."""
        return self._location_note

    @property
    def physical_condition(self) -> PhysicalCopyCondition:
        """État matériel observé."""
        return self._physical_condition

    @property
    def business_status(self) -> PhysicalCopyBusinessStatus:
        """Statut métier."""
        return self._business_status

    @property
    def language(self) -> str | None:
        """Langue de l'exemplaire si renseignée."""
        return self._language

    @property
    def finish(self) -> str | None:
        """Finition (holo, textured, etc.)."""
        return self._finish

    @property
    def notes(self) -> str | None:
        """Annotations libres."""
        return self._notes

    @property
    def is_logically_deleted(self) -> bool:
        """Vrai si la copie a été supprimée logiquement (horodatage de fin)."""
        return self._metadata.timestamps.deleted_at is not None

    @classmethod
    def create(  # pylint: disable=too-many-arguments
        cls,
        entity_id: DomainId,
        card_id: DomainId,
        owner_user_id: DomainId,
        metadata: EntityMetadata,
        *,
        physical_condition: PhysicalCopyCondition,
        business_status: PhysicalCopyBusinessStatus,
        container_id: DomainId | None = None,
        location_note: str | None = None,
        language: str | None = None,
        finish: str | None = None,
        notes: str | None = None,
    ) -> PhysicalCopy:
        """Instancie une copie cohérente avec ses métadonnées d'origine."""
        return cls(
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

    def update_details(  # pylint: disable=too-many-locals
        self,
        moment: datetime,
        *,
        location_note: str | None | Any = UNSET,
        language: str | None | Any = UNSET,
        finish: str | None | Any = UNSET,
        notes: str | None | Any = UNSET,
    ) -> None:
        """Met à jour les champs descriptifs optionnels (absent = inchangé)."""
        self._ensure_not_deleted()
        candidate_location = (
            self._location_note
            if location_note is UNSET
            else PhysicalCopy._optional_inline(location_note, "location_note", _MAX_LOCATION_LEN)
        )
        candidate_language = (
            self._language
            if language is UNSET
            else PhysicalCopy._optional_inline(language, "language", _MAX_LANGUAGE_LEN)
        )
        candidate_finish = (
            self._finish
            if finish is UNSET
            else PhysicalCopy._optional_inline(finish, "finish", _MAX_FINISH_LEN)
        )
        candidate_notes = (
            self._notes
            if notes is UNSET
            else PhysicalCopy._optional_inline(notes, "notes", _MAX_NOTES_LEN)
        )
        unchanged = (
            candidate_location == self._location_note
            and candidate_language == self._language
            and candidate_finish == self._finish
            and candidate_notes == self._notes
        )
        if unchanged:
            return
        self._bump_dirty(moment)
        self._location_note = candidate_location
        self._language = candidate_language
        self._finish = candidate_finish
        self._notes = candidate_notes

    def change_physical_condition(self, moment: datetime, condition: PhysicalCopyCondition) -> None:
        """Remplace l'état matériel et trace la mutation."""
        self._ensure_not_deleted()
        if condition is self._physical_condition:
            return
        self._bump_dirty(moment)
        self._physical_condition = condition

    def change_business_status(
        self,
        moment: datetime,
        status: PhysicalCopyBusinessStatus,
    ) -> None:
        """Met à jour le statut métier courant."""
        self._ensure_not_deleted()
        if status is self._business_status:
            return
        self._bump_dirty(moment)
        self._business_status = status

    def attach_to_container(self, moment: datetime, container_id: DomainId) -> None:
        """Rattache l'exemplaire à un contenant (remplace le contenant précédent)."""
        self._ensure_not_deleted()
        if self._container_id is not None and self._container_id.value == container_id.value:
            return
        self._bump_dirty(moment)
        self._container_id = container_id

    def detach_from_container(self, moment: datetime) -> None:
        """Retire le rattachement à un contenant."""
        self._ensure_not_deleted()
        if self._container_id is None:
            return
        self._bump_dirty(moment)
        self._container_id = None

    def soft_delete(self, moment: datetime) -> None:
        """Supprime logiquement la copie (préféré à une destruction physique)."""
        if self.is_logically_deleted:
            raise InvalidPhysicalCopyException("La copie est déjà supprimée logiquement.")
        new_meta = self._metadata.mark_deleted(moment)
        self.replace_metadata(new_meta)

    def _bump_dirty(self, moment: datetime) -> None:
        new_meta = self._metadata.bump_version(moment).with_sync_state(SyncState.DIRTY)
        self.replace_metadata(new_meta)

    def _ensure_not_deleted(self) -> None:
        if self.is_logically_deleted:
            raise InvalidPhysicalCopyException(
                "La copie est supprimée logiquement et ne peut plus être modifiée."
            )

    @staticmethod
    def _optional_text(value: str | None, field: str, max_len: int) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            return None
        if len(stripped) > max_len:
            raise InvalidPhysicalCopyException(
                f"Le champ {field} ne peut pas dépasser {max_len} caractères."
            )
        return stripped

    @staticmethod
    def _optional_inline(value: str | None, field: str, max_len: int) -> str | None:
        return PhysicalCopy._optional_text(value, field, max_len)
