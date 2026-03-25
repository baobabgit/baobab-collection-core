"""Cas d'usage applicatifs pour les contenants de rangement."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.container import Container
from baobab_collection_core.domain.container_kind import ContainerKind
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.container_cycle_exception import ContainerCycleException
from baobab_collection_core.exceptions.container_not_found_exception import (
    ContainerNotFoundException,
)
from baobab_collection_core.exceptions.invalid_container_exception import InvalidContainerException
from baobab_collection_core.ports.container_repository_port import ContainerRepositoryPort


class ContainerApplicationService:
    """Orchestration des contenants et de la hiérarchie sans cycles.

    :param containers: Port de persistance injecté.
    """

    __slots__ = ("_containers",)

    def __init__(self, containers: ContainerRepositoryPort) -> None:
        self._containers = containers

    def create_container(
        self,
        name: str,
        kind: ContainerKind,
        moment: datetime,
        *,
        parent_id: DomainId | None = None,
    ) -> Container:
        """Crée un contenant racine ou rattaché à un parent actif."""
        Container.validate_name(name)
        if parent_id is not None:
            parent = self._require_container(parent_id)
            self._require_not_archived_for_structure(parent)
        entity_id = DomainId(str(uuid.uuid4()))
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.DIRTY,
        )
        container = Container.create(entity_id, name, kind, metadata, parent_id=parent_id)
        self._containers.save(container)
        return container

    def update_container(
        self,
        container_id: DomainId,
        moment: datetime,
        *,
        name: str | None = None,
        kind: ContainerKind | None = None,
    ) -> Container:
        """Met à jour nom et/ou type (champs ``None`` laissés inchangés)."""
        container = self._require_container(container_id)
        container.update(moment, name=name, kind=kind)
        self._containers.save(container)
        return container

    def archive_container(self, container_id: DomainId, moment: datetime) -> Container:
        """Archive un contenant (figé, consultable)."""
        container = self._require_container(container_id)
        container.archive(moment)
        self._containers.save(container)
        return container

    def attach_to_parent(
        self,
        container_id: DomainId,
        parent_id: DomainId,
        moment: datetime,
    ) -> Container:
        """Rattache un contenant actif sous un parent actif (vérifie l'acyclicité)."""
        if parent_id.value == container_id.value:
            raise ContainerCycleException("Un contenant ne peut pas être son propre parent.")
        container = self._require_container(container_id)
        parent = self._require_container(parent_id)
        self._require_not_archived_for_structure(container)
        self._require_not_archived_for_structure(parent)
        self._assert_reparent_acyclic(container, parent_id)
        container.set_parent(moment, parent_id)
        self._containers.save(container)
        return container

    def move_container(
        self,
        container_id: DomainId,
        new_parent_id: DomainId | None,
        moment: datetime,
    ) -> Container:
        """Déplace un contenant vers un nouveau parent ou à la racine."""
        container = self._require_container(container_id)
        self._require_not_archived_for_structure(container)
        if new_parent_id is not None:
            parent = self._require_container(new_parent_id)
            self._require_not_archived_for_structure(parent)
            self._assert_reparent_acyclic(container, new_parent_id)
        container.set_parent(moment, new_parent_id)
        self._containers.save(container)
        return container

    def list_children(self, parent_id: DomainId) -> Sequence[Container]:
        """Liste les enfants directs d'un parent (tous états)."""
        _ = self._require_container(parent_id)
        return self._containers.list_direct_children(parent_id)

    def get_container(self, container_id: DomainId) -> Container:
        """Retourne un contenant existant."""
        return self._require_container(container_id)

    def _require_container(self, container_id: DomainId) -> Container:
        found = self._containers.get_by_id(container_id)
        if found is None:
            raise ContainerNotFoundException(
                "Aucun contenant ne correspond à l'identifiant fourni dans la collection."
            )
        return found

    @staticmethod
    def _require_not_archived_for_structure(container: Container) -> None:
        if container.is_archived:
            raise InvalidContainerException(
                "Un contenant archivé ne peut pas être utilisé dans cette opération."
            )

    def _assert_reparent_acyclic(self, container: Container, new_parent_id: DomainId) -> None:
        """Vérifie que ``new_parent_id`` n'est pas ce contenant ni l'un de ses descendants."""
        chain = self._ancestor_id_chain_upward(new_parent_id)
        if container.entity_id.value in chain:
            raise ContainerCycleException(
                "Ce rattachement créerait un cycle dans la hiérarchie des contenants."
            )

    def _ancestor_id_chain_upward(self, start: DomainId) -> list[str]:
        """Chaîne d'identifiants du nœud ``start`` jusqu'à la racine (inclus)."""
        ordered: list[str] = []
        visited: set[str] = set()
        current: DomainId | None = start
        while current is not None:
            if current.value in visited:
                raise InvalidContainerException(
                    "Hiérarchie des contenants incohérente (cycle stocké détecté)."
                )
            visited.add(current.value)
            ordered.append(current.value)
            node = self._containers.get_by_id(current)
            if node is None:
                raise ContainerNotFoundException(
                    "Chaîne de parents interrompue : contenant parent introuvable."
                )
            current = node.parent_id
        return ordered
