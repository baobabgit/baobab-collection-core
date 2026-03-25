"""Tests applicatifs du service exemplaires physiques."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.application.physical_copy_application_service import (
    PhysicalCopyApplicationService,
)
from baobab_collection_core.domain.collection_card import UNSET
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.physical_copy_business_status import PhysicalCopyBusinessStatus
from baobab_collection_core.domain.physical_copy_condition import PhysicalCopyCondition
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions import (
    InvalidPhysicalCopyException,
    PhysicalCopyNotFoundException,
)
from tests.baobab_collection_core.support.in_memory_physical_copy_repository import (
    InMemoryPhysicalCopyRepository,
)


class TestPhysicalCopyApplicationService:
    """Scénarios de création, lecture, transitions et liste."""

    @staticmethod
    def _moment() -> datetime:
        return datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)

    @staticmethod
    def _card_id() -> DomainId:
        return DomainId("00000000-0000-4000-8000-00000000c4d0")

    @staticmethod
    def _owner_id() -> DomainId:
        return DomainId("11111111-1111-4111-8111-111111111111")

    def _svc(self) -> tuple[PhysicalCopyApplicationService, InMemoryPhysicalCopyRepository]:
        repo = InMemoryPhysicalCopyRepository()
        return PhysicalCopyApplicationService(repo), repo

    def test_create_nominal(self) -> None:
        """Création avec état initial DIRTY et version 0."""
        svc, _ = self._svc()
        copy = svc.create_copy(
            self._card_id(),
            self._owner_id(),
            self._moment(),
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
            location_note="  Étagère 1  ",
        )
        assert copy.metadata.sync_state is SyncState.DIRTY
        assert copy.metadata.version.value == 0
        assert copy.location_note == "Étagère 1"

    def test_create_invalid_notes_domain(self) -> None:
        """Les validations remontent pour les champs trop longs."""
        svc, _ = self._svc()
        with pytest.raises(InvalidPhysicalCopyException):
            svc.create_copy(
                self._card_id(),
                self._owner_id(),
                self._moment(),
                physical_condition=PhysicalCopyCondition.UNKNOWN,
                business_status=PhysicalCopyBusinessStatus.ACTIVE,
                notes="n" * 4001,
            )

    def test_get_not_found_missing(self) -> None:
        """Identifiant inconnu -> exception dédiée."""
        svc, _ = self._svc()
        with pytest.raises(PhysicalCopyNotFoundException):
            svc.get_copy_by_id(DomainId("99999999-9999-4999-8999-999999999999"))

    def test_get_not_found_when_soft_deleted(self) -> None:
        """Copie supprimée traitée comme absente pour les opérations actives."""
        svc, repo = self._svc()
        created = svc.create_copy(
            self._card_id(),
            self._owner_id(),
            self._moment(),
            physical_condition=PhysicalCopyCondition.NEAR_MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
        )
        svc.soft_delete_copy(created.entity_id, self._moment() + timedelta(minutes=1))
        assert repo.get_by_id(created.entity_id) is not None
        with pytest.raises(PhysicalCopyNotFoundException):
            svc.get_copy_by_id(created.entity_id)

    def test_attach_and_detach_container(self) -> None:
        """Rattachement puis détachement persistés."""
        svc, _ = self._svc()
        copy = svc.create_copy(
            self._card_id(),
            self._owner_id(),
            self._moment(),
            physical_condition=PhysicalCopyCondition.LIGHT_PLAYED,
            business_status=PhysicalCopyBusinessStatus.FOR_TRADE,
        )
        box = DomainId("33333333-3333-4333-8333-333333333333")
        m1 = self._moment() + timedelta(minutes=2)
        attached = svc.attach_container(copy.entity_id, m1, box)
        assert attached.container_id == box
        m2 = m1 + timedelta(minutes=1)
        detached = svc.detach_container(copy.entity_id, m2)
        assert detached.container_id is None

    def test_soft_delete_copy(self) -> None:
        """Suppression logique et sauvegarde."""
        svc, _ = self._svc()
        copy = svc.create_copy(
            self._card_id(),
            self._owner_id(),
            self._moment(),
            physical_condition=PhysicalCopyCondition.PLAYED,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
        )
        deleted = svc.soft_delete_copy(copy.entity_id, self._moment() + timedelta(hours=1))
        assert deleted.is_logically_deleted is True

    def test_list_copies_for_card_excludes_deleted(self) -> None:
        """Liste par carte : uniquement les exemplaires actifs."""
        svc, _ = self._svc()
        c1 = svc.create_copy(
            self._card_id(),
            self._owner_id(),
            self._moment(),
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
        )
        c2 = svc.create_copy(
            self._card_id(),
            self._owner_id(),
            self._moment() + timedelta(seconds=1),
            physical_condition=PhysicalCopyCondition.POOR,
            business_status=PhysicalCopyBusinessStatus.ARCHIVED,
        )
        svc.soft_delete_copy(c2.entity_id, self._moment() + timedelta(hours=2))
        active = svc.list_copies_for_card(self._card_id())
        assert len(active) == 1
        assert active[0].entity_id == c1.entity_id

    def test_update_change_status_and_condition(self) -> None:
        """Mise à jour partielle + changements d'état."""
        svc, _ = self._svc()
        copy = svc.create_copy(
            self._card_id(),
            self._owner_id(),
            self._moment(),
            physical_condition=PhysicalCopyCondition.UNKNOWN,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
            finish="matte",
        )
        m = self._moment() + timedelta(minutes=5)
        svc.update_copy_details(copy.entity_id, m, notes="ok", language="en", finish=UNSET)
        svc.change_physical_condition(
            copy.entity_id, m + timedelta(seconds=1), PhysicalCopyCondition.MINT
        )
        svc.change_business_status(
            copy.entity_id,
            m + timedelta(seconds=2),
            PhysicalCopyBusinessStatus.ON_LOAN,
        )
        refreshed = svc.get_copy_by_id(copy.entity_id)
        assert refreshed.notes == "ok"
        assert refreshed.language == "en"
        assert refreshed.finish == "matte"
        assert refreshed.physical_condition is PhysicalCopyCondition.MINT
        assert refreshed.business_status is PhysicalCopyBusinessStatus.ON_LOAN
