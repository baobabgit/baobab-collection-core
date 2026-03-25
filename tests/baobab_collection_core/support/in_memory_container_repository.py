"""Implémentation mémoire de :class:`ContainerRepositoryPort`."""

from __future__ import annotations

from collections.abc import Sequence

from baobab_collection_core.domain.container import Container
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.ports.container_repository_port import ContainerRepositoryPort


class InMemoryContainerRepository(ContainerRepositoryPort):
    """Stockage volatile des contenants."""

    __slots__ = ("_storage",)

    def __init__(self) -> None:
        self._storage: dict[str, Container] = {}

    def get_by_id(self, container_id: DomainId) -> Container | None:
        """Voir :meth:`ContainerRepositoryPort.get_by_id`."""
        return self._storage.get(container_id.value)

    def list_direct_children(self, parent_id: DomainId) -> Sequence[Container]:
        """Filtre par ``parent_id`` avec tri déterministe."""
        return tuple(
            sorted(
                (
                    c
                    for c in self._storage.values()
                    if c.parent_id is not None and c.parent_id.value == parent_id.value
                ),
                key=lambda item: item.entity_id.value,
            )
        )

    def save(self, container: Container) -> None:
        """Upsert."""
        self._storage[container.entity_id.value] = container
