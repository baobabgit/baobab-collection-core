"""Base minimaliste pour les futures entités de collection."""

from __future__ import annotations

from abc import ABC

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata


class EntityBase(ABC):
    """Superclasse avec identifiant stable et métadonnées versionnées.

    Ne contient pas de logique métier : sert d'ancre pour cartes, copies, contenants, etc.
    Les sous-classes ajoutent invariants et comportements spécifiques.

    :param entity_id: Identifiant immuable de la ressource.
    :param metadata: Agrégat de synchro, audit et version.

    :ivar _entity_id: Stockage interne de l'identifiant (protégé conceptuellement).
    :ivar _metadata: Stockage interne des métadonnées.
    """

    __slots__ = ("_entity_id", "_metadata")

    def __init__(self, entity_id: DomainId, metadata: EntityMetadata) -> None:
        self._entity_id = entity_id
        self._metadata = metadata

    @property
    def entity_id(self) -> DomainId:
        """Identifiant de domaine."""
        return self._entity_id

    @property
    def metadata(self) -> EntityMetadata:
        """Métadonnées courantes (immutables ; remplacer l'instance entière)."""
        return self._metadata

    def replace_metadata(self, metadata: EntityMetadata) -> None:
        """Remplace le bundle de métadonnées en empêchant une régression de version.

        :param metadata: Nouveau value object :class:`EntityMetadata`.
        :raises ValidationException: si la version diminue (module ``validation_exception``).
        """
        metadata.require_monotone_version(self._metadata.version)
        self._metadata = metadata
