"""Tests applicatifs du service contenants."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.application.container_application_service import (
    ContainerApplicationService,
)
from baobab_collection_core.domain.container_kind import ContainerKind
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.exceptions import (
    ContainerCycleException,
    ContainerNotFoundException,
    InvalidContainerException,
)
from tests.baobab_collection_core.support.in_memory_container_repository import (
    InMemoryContainerRepository,
)


class TestContainerApplicationService:
    """Hiérarchie, archivage et détection de cycles."""

    @staticmethod
    def _moment() -> datetime:
        return datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)

    def _svc(self) -> tuple[ContainerApplicationService, InMemoryContainerRepository]:
        repo = InMemoryContainerRepository()
        return ContainerApplicationService(repo), repo

    def test_create_nominal_root(self) -> None:
        """Création racine : état synchro initial."""
        svc, _ = self._svc()
        c = svc.create_container("  Boîte 1  ", ContainerKind.BOX, self._moment())
        assert c.name == "Boîte 1"
        assert c.parent_id is None
        assert c.metadata.sync_state.value == "dirty"

    def test_create_under_parent(self) -> None:
        """Enfant rattaché au parent créé."""
        svc, _ = self._svc()
        parent = svc.create_container("Parent", ContainerKind.BINDER, self._moment())
        child = svc.create_container(
            "Enfant",
            ContainerKind.DECK_BOX,
            self._moment() + timedelta(seconds=1),
            parent_id=parent.entity_id,
        )
        assert child.parent_id == parent.entity_id

    def test_create_under_archived_parent_raises(self) -> None:
        """Impossible de créer sous un parent archivé."""
        svc, _ = self._svc()
        parent = svc.create_container("Vieux", ContainerKind.STACK, self._moment())
        svc.archive_container(parent.entity_id, self._moment() + timedelta(minutes=1))
        with pytest.raises(InvalidContainerException):
            svc.create_container(
                "Nouveau",
                ContainerKind.BOX,
                self._moment() + timedelta(minutes=2),
                parent_id=parent.entity_id,
            )

    def test_update_container(self) -> None:
        """Modification du nom et du type."""
        svc, _ = self._svc()
        c = svc.create_container("A", ContainerKind.BOX, self._moment())
        updated = svc.update_container(
            c.entity_id,
            self._moment() + timedelta(minutes=5),
            name="B",
            kind=ContainerKind.TEMP_ZONE,
        )
        assert updated.name == "B"
        assert updated.kind is ContainerKind.TEMP_ZONE

    def test_move_to_root(self) -> None:
        """Déplacement à la racine."""
        svc, _ = self._svc()
        parent = svc.create_container("P", ContainerKind.BOX, self._moment())
        child = svc.create_container(
            "C",
            ContainerKind.STACK,
            self._moment() + timedelta(seconds=1),
            parent_id=parent.entity_id,
        )
        moved = svc.move_container(child.entity_id, None, self._moment() + timedelta(minutes=1))
        assert moved.parent_id is None

    def test_attach_to_parent_valid(self) -> None:
        """Changement de parent valide."""
        svc, _ = self._svc()
        p1 = svc.create_container("P1", ContainerKind.BOX, self._moment())
        p2 = svc.create_container("P2", ContainerKind.BOX, self._moment() + timedelta(seconds=1))
        child = svc.create_container(
            "C",
            ContainerKind.DECK_BOX,
            self._moment() + timedelta(seconds=2),
            parent_id=p1.entity_id,
        )
        attached = svc.attach_to_parent(
            child.entity_id,
            p2.entity_id,
            self._moment() + timedelta(minutes=10),
        )
        assert attached.parent_id == p2.entity_id

    def test_cycle_detection_descendant_as_parent(self) -> None:
        """A → B → C : rattacher A sous C crée un cycle."""
        svc, _ = self._svc()
        a = svc.create_container("A", ContainerKind.LOGICAL_GROUP, self._moment())
        b = svc.create_container(
            "B",
            ContainerKind.LOGICAL_GROUP,
            self._moment() + timedelta(seconds=1),
            parent_id=a.entity_id,
        )
        c = svc.create_container(
            "C",
            ContainerKind.LOGICAL_GROUP,
            self._moment() + timedelta(seconds=2),
            parent_id=b.entity_id,
        )
        with pytest.raises(ContainerCycleException):
            svc.move_container(a.entity_id, c.entity_id, self._moment() + timedelta(minutes=1))

    def test_attach_self_raises(self) -> None:
        """Un contenant ne peut pas être son propre parent."""
        svc, _ = self._svc()
        c = svc.create_container("Seul", ContainerKind.BOX, self._moment())
        with pytest.raises(ContainerCycleException):
            svc.attach_to_parent(c.entity_id, c.entity_id, self._moment() + timedelta(minutes=1))

    def test_list_children_direct(self) -> None:
        """Lecture des enfants directs."""
        svc, _ = self._svc()
        parent = svc.create_container("P", ContainerKind.BINDER, self._moment())
        svc.create_container(
            "E1",
            ContainerKind.BOX,
            self._moment() + timedelta(seconds=1),
            parent_id=parent.entity_id,
        )
        svc.create_container(
            "E2",
            ContainerKind.BOX,
            self._moment() + timedelta(seconds=2),
            parent_id=parent.entity_id,
        )
        kids = list(svc.list_children(parent.entity_id))
        assert len(kids) == 2
        names = {k.name for k in kids}
        assert names == {"E1", "E2"}

    def test_list_children_parent_missing(self) -> None:
        """Parent inconnu : erreur explicite."""
        svc, _ = self._svc()
        missing = DomainId("99999999-9999-4999-8999-999999999999")
        with pytest.raises(ContainerNotFoundException):
            _ = svc.list_children(missing)

    def test_archive_container(self) -> None:
        """Archivage persisté."""
        svc, _ = self._svc()
        c = svc.create_container("Z", ContainerKind.TEMP_ZONE, self._moment())
        archived = svc.archive_container(c.entity_id, self._moment() + timedelta(hours=1))
        assert archived.is_archived is True
