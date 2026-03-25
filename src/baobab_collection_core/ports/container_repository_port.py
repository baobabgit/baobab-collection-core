"""Contrat de persistance pour :class:`~baobab_collection_core.domain.container.Container`."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from baobab_collection_core.domain.container import Container
from baobab_collection_core.domain.domain_id import DomainId


class ContainerRepositoryPort(ABC):
    """Accès aux contenants sans technologie de stockage imposée."""

    @abstractmethod
    def get_by_id(self, container_id: DomainId) -> Container | None:
        """Retourne le contenant ou ``None``."""

    @abstractmethod
    def list_direct_children(self, parent_id: DomainId) -> Sequence[Container]:
        """Enfants directs du parent donné (parenté par ``parent_id``)."""

    @abstractmethod
    def save(self, container: Container) -> None:
        """Crée ou met à jour le contenant."""
