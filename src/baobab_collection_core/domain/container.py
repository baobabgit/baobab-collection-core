"""Entité métier : contenant de rangement (hiérarchie parent / enfant)."""

from __future__ import annotations

from datetime import datetime

from baobab_collection_core.domain.container_kind import ContainerKind
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_base import EntityBase
from baobab_collection_core.domain.entity_lifecycle_state import EntityLifecycleState
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.container_cycle_exception import ContainerCycleException
from baobab_collection_core.exceptions.invalid_container_exception import InvalidContainerException

_MAX_NAME_LEN = 256


class Container(EntityBase):
    """Contenant nommé, typé, optionnellement rattaché à un parent.

    L'``entity_id`` pourra être référencé par les exemplaires physiques (``container_id``).
    L'archivage fige le contenant sans le détruire (historisation).

    :param entity_id: Identifiant stable du contenant.
    :param name: Libellé affiché (non vide après normalisation).
    :param kind: Type de contenant (:class:`ContainerKind`).
    :param metadata: Audit, version optimiste et synchro (cycle de vie actif/archivé).
    :param parent_id: Contenant parent ou ``None`` pour une racine.
    """

    __slots__ = ("_name", "_kind", "_parent_id")

    def __init__(
        self,
        entity_id: DomainId,
        name: str,
        kind: ContainerKind,
        metadata: EntityMetadata,
        *,
        parent_id: DomainId | None = None,
    ) -> None:
        Container._validate_name(name)
        super().__init__(entity_id, metadata)
        self._name = name.strip()
        self._kind = kind
        self._parent_id = parent_id

    @property
    def name(self) -> str:
        """Nom du contenant."""
        return self._name

    @property
    def kind(self) -> ContainerKind:
        """Type de rangement."""
        return self._kind

    @property
    def parent_id(self) -> DomainId | None:
        """Parent direct, ou ``None``."""
        return self._parent_id

    @property
    def is_archived(self) -> bool:
        """Vrai si le contenant est archivé (figé, conservé pour l'historique)."""
        return self._metadata.lifecycle_state is EntityLifecycleState.ARCHIVED

    @classmethod
    def create(
        cls,
        entity_id: DomainId,
        name: str,
        kind: ContainerKind,
        metadata: EntityMetadata,
        *,
        parent_id: DomainId | None = None,
    ) -> Container:
        """Instancie un contenant cohérent avec ses métadonnées initiales."""
        return cls(entity_id, name, kind, metadata, parent_id=parent_id)

    @staticmethod
    def validate_name(name: str) -> None:
        """Valide un nom hors contexte d'entité (services applicatifs).

        :raises InvalidContainerException: si le texte est invalide.
        """
        Container._validate_name(name)

    @staticmethod
    def _validate_name(name: str) -> None:
        stripped = name.strip()
        if not stripped:
            raise InvalidContainerException("Le nom du contenant ne peut pas être vide.")
        if len(stripped) > _MAX_NAME_LEN:
            raise InvalidContainerException(
                f"Le nom du contenant ne peut pas dépasser {_MAX_NAME_LEN} caractères."
            )

    def update(  # pylint: disable=too-many-arguments
        self,
        moment: datetime,
        *,
        name: str | None = None,
        kind: ContainerKind | None = None,
    ) -> None:
        """Met à jour le nom et/ou le type (arguments ``None`` = inchangé)."""
        self._ensure_active_for_mutation()
        candidate_name = self._name if name is None else Container._validated_name_value(name)
        candidate_kind = self._kind if kind is None else kind
        if candidate_name == self._name and candidate_kind is self._kind:
            return
        self._bump_dirty(moment)
        self._name = candidate_name
        self._kind = candidate_kind

    def set_parent(self, moment: datetime, new_parent_id: DomainId | None) -> None:
        """Assigne le parent direct après contrôle d'acyclicité externe.

        :param new_parent_id: Nouveau parent ou ``None`` pour la racine.
        :raises InvalidContainerException: si le contenant est archivé.
        :raises ContainerCycleException: si ``new_parent_id`` est ce contenant lui-même.
        """
        self._ensure_active_for_mutation()
        if new_parent_id is not None and new_parent_id.value == self.entity_id.value:
            raise ContainerCycleException("Un contenant ne peut pas être son propre parent.")
        if self._parent_id is None and new_parent_id is None:
            return
        if (
            self._parent_id is not None
            and new_parent_id is not None
            and self._parent_id.value == new_parent_id.value
        ):
            return
        self._bump_dirty(moment)
        self._parent_id = new_parent_id

    def archive(self, moment: datetime) -> None:
        """Archive le contenant (invariant : ne modifie pas la parenté)."""
        if self.is_archived:
            raise InvalidContainerException("Le contenant est déjà archivé.")
        new_meta = (
            self._metadata.bump_version(moment)
            .with_sync_state(SyncState.DIRTY)
            .with_lifecycle_state(EntityLifecycleState.ARCHIVED)
        )
        self.replace_metadata(new_meta)

    def _ensure_active_for_mutation(self) -> None:
        if self.is_archived:
            raise InvalidContainerException(
                "Le contenant est archivé et ne peut pas être modifié structurellement."
            )

    def _bump_dirty(self, moment: datetime) -> None:
        new_meta = self._metadata.bump_version(moment).with_sync_state(SyncState.DIRTY)
        self.replace_metadata(new_meta)

    @staticmethod
    def _validated_name_value(name: str) -> str:
        Container._validate_name(name)
        return name.strip()
