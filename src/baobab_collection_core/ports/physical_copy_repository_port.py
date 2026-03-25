"""Contrat de persistance pour les exemplaires physiques (:class:`PhysicalCopy`)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.physical_copy import PhysicalCopy


class PhysicalCopyRepositoryPort(ABC):
    """Accès aux exemplaires physiques sans technology lock-in."""

    @abstractmethod
    def get_by_id(self, copy_id: DomainId) -> PhysicalCopy | None:
        """Retourne la copie ou ``None``."""

    @abstractmethod
    def list_by_card_id(self, card_id: DomainId) -> Sequence[PhysicalCopy]:
        """Toutes les copies liées à une carte (y compris supprimées logiquement)."""

    @abstractmethod
    def save(self, physical_copy: PhysicalCopy) -> None:
        """Crée ou met à jour la copie."""
