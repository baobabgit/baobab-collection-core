"""Implémentation mémoire de :class:`PhysicalCopyRepositoryPort`."""

from __future__ import annotations

from collections.abc import Sequence

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.physical_copy import PhysicalCopy
from baobab_collection_core.ports.physical_copy_repository_port import PhysicalCopyRepositoryPort


class InMemoryPhysicalCopyRepository(PhysicalCopyRepositoryPort):
    """Stockage volatile des exemplaires physiques."""

    __slots__ = ("_storage",)

    def __init__(self) -> None:
        self._storage: dict[str, PhysicalCopy] = {}

    def get_by_id(self, copy_id: DomainId) -> PhysicalCopy | None:
        """Voir :meth:`PhysicalCopyRepositoryPort.get_by_id`."""
        return self._storage.get(copy_id.value)

    def list_by_card_id(self, card_id: DomainId) -> Sequence[PhysicalCopy]:
        """Filtre toutes les copies liées à ``card_id`` (tri déterministe)."""
        return tuple(
            sorted(
                (c for c in self._storage.values() if c.card_id.value == card_id.value),
                key=lambda item: item.entity_id.value,
            )
        )

    def save(self, physical_copy: PhysicalCopy) -> None:
        """Upsert."""
        self._storage[physical_copy.entity_id.value] = physical_copy
