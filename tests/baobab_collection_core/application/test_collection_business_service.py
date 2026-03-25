"""Tests du service métier de collection (agrégats, localisation, doublons)."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.application.card_application_service import CardApplicationService
from baobab_collection_core.application.collection_business_service import CollectionBusinessService
from baobab_collection_core.application.container_application_service import (
    ContainerApplicationService,
)
from baobab_collection_core.application.physical_copy_application_service import (
    PhysicalCopyApplicationService,
)
from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.collection_card import CollectionCard
from baobab_collection_core.domain.container_kind import ContainerKind
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.physical_copy_business_status import PhysicalCopyBusinessStatus
from baobab_collection_core.domain.physical_copy_condition import PhysicalCopyCondition
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions import (
    CardNotFoundException,
    ContainerNotFoundException,
    PhysicalCopyNotFoundException,
)
from tests.baobab_collection_core.support.in_memory_card_repository import InMemoryCardRepository
from tests.baobab_collection_core.support.in_memory_container_repository import (
    InMemoryContainerRepository,
)
from tests.baobab_collection_core.support.in_memory_physical_copy_repository import (
    InMemoryPhysicalCopyRepository,
)


class TestCollectionBusinessService:
    """Intégration légère cartes / copies / contenants."""

    @staticmethod
    def _moment() -> datetime:
        return datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)

    def _services(
        self,
    ) -> tuple[
        CollectionBusinessService,
        CardApplicationService,
        PhysicalCopyApplicationService,
        ContainerApplicationService,
    ]:
        cards = InMemoryCardRepository()
        copies = InMemoryPhysicalCopyRepository()
        containers = InMemoryContainerRepository()
        biz = CollectionBusinessService(cards, copies, containers)
        return (
            biz,
            CardApplicationService(cards),
            PhysicalCopyApplicationService(copies),
            ContainerApplicationService(containers),
        )

    def test_counts_nominal(self) -> None:
        """Comptages cartes distinctes, totaux inventaire, disponibles."""
        biz, cards, copies_s, _ = self._services()
        t0 = self._moment()
        ca = cards.create_card("Alpha", t0)
        cb = cards.create_card("Beta", t0 + timedelta(seconds=1))
        copies_s.create_copy(
            ca.entity_id,
            DomainId("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
            t0,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
        )
        copies_s.create_copy(
            ca.entity_id,
            DomainId("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
            t0 + timedelta(seconds=1),
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ON_LOAN,
        )
        copies_s.create_copy(
            cb.entity_id,
            DomainId("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
            t0 + timedelta(seconds=2),
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.FOR_TRADE,
        )
        assert biz.count_distinct_cards_in_collection() == 2
        assert biz.count_total_copies_in_inventory() == 3
        assert biz.count_available_copies() == 2

    def test_soft_deleted_excluded_from_counts(self) -> None:
        """Copies supprimées logiquement exclues des agrégats."""
        biz, cards, copies_s, _ = self._services()
        t0 = self._moment()
        c = cards.create_card("Gamma", t0)
        cp = copies_s.create_copy(
            c.entity_id,
            DomainId("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
            t0,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
        )
        copies_s.soft_delete_copy(cp.entity_id, t0 + timedelta(hours=1))
        assert biz.count_total_copies_in_inventory() == 0
        assert biz.count_distinct_cards_in_collection() == 0

    def test_get_copy_location_unknown_container_id_returns_no_name(self) -> None:
        """Référence de contenant orpheline : identifiant conservé, nom absent."""
        biz, cards, copies_s, _ = self._services()
        t0 = self._moment()
        card = cards.create_card("Orphelin", t0)
        ghost = DomainId("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
        cp = copies_s.create_copy(
            card.entity_id,
            DomainId("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
            t0,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
            container_id=ghost,
        )
        loc = biz.get_copy_location(cp.entity_id)
        assert loc.container_id == ghost
        assert loc.container_name is None

    def test_get_copy_location_resolves_container_name(self) -> None:
        """Localisation avec nom de contenant résolu."""
        biz, cards, copies_s, cont_s = self._services()
        t0 = self._moment()
        box = cont_s.create_container("Boîte A", ContainerKind.BOX, t0)
        card = cards.create_card("Carte X", t0)
        cp = copies_s.create_copy(
            card.entity_id,
            DomainId("cccccccc-cccc-4ccc-8ccc-cccccccccccc"),
            t0,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
            location_note="  Tiroir  ",
        )
        copies_s.attach_container(cp.entity_id, t0 + timedelta(minutes=1), box.entity_id)
        loc = biz.get_copy_location(cp.entity_id)
        assert loc.container_id == box.entity_id
        assert loc.container_name == "Boîte A"
        assert loc.location_note == "Tiroir"

    def test_get_copy_location_not_found(self) -> None:
        """Copie absente : exception."""
        biz, *_ = self._services()
        missing = DomainId("99999999-9999-4999-8999-999999999999")
        with pytest.raises(PhysicalCopyNotFoundException):
            biz.get_copy_location(missing)

    def test_get_copy_location_soft_deleted_raises(self) -> None:
        """Copie supprimée logiquement : pas de localisation."""
        biz, cards, copies_s, _ = self._services()
        t0 = self._moment()
        card = cards.create_card("Y", t0)
        cp = copies_s.create_copy(
            card.entity_id,
            DomainId("ffffffff-ffff-4fff-8fff-ffffffffffff"),
            t0,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
        )
        copies_s.soft_delete_copy(cp.entity_id, t0 + timedelta(minutes=1))
        with pytest.raises(PhysicalCopyNotFoundException):
            biz.get_copy_location(cp.entity_id)

    def test_list_active_copies_for_card_requires_card(self) -> None:
        """Carte inconnue : erreur métier."""
        biz, *_ = self._services()
        with pytest.raises(CardNotFoundException):
            biz.list_active_copies_for_card(DomainId("99999999-9999-4999-8999-999999999999"))

    def test_list_container_contents(self) -> None:
        """Contenu : sous-contenants + copies actives dans le contenant."""
        biz, cards, copies_s, cont_s = self._services()
        t0 = self._moment()
        parent = cont_s.create_container("Parent", ContainerKind.BINDER, t0)
        child = cont_s.create_container(
            "Enfant",
            ContainerKind.BOX,
            t0 + timedelta(seconds=1),
            parent_id=parent.entity_id,
        )
        card = cards.create_card("Dans la boîte", t0)
        cp = copies_s.create_copy(
            card.entity_id,
            DomainId("dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
            t0,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
        )
        copies_s.attach_container(cp.entity_id, t0 + timedelta(minutes=2), child.entity_id)
        view = biz.list_container_contents(child.entity_id)
        assert len(view.child_containers) == 0
        assert len(view.physical_copies) == 1
        assert view.physical_copies[0].entity_id == cp.entity_id
        parent_view = biz.list_container_contents(parent.entity_id)
        assert len(parent_view.child_containers) == 1
        assert len(parent_view.physical_copies) == 0

    def test_list_container_missing_raises(self) -> None:
        """Contenant inconnu."""
        biz, *_ = self._services()
        with pytest.raises(ContainerNotFoundException):
            biz.list_container_contents(DomainId("88888888-8888-4888-8888-888888888888"))

    def test_duplicate_catalog_cards_by_external_id(self) -> None:
        """Deux entrées catalogue avec même identifiant externe normalisé."""
        cards_repo = InMemoryCardRepository()
        copies_repo = InMemoryPhysicalCopyRepository()
        containers_repo = InMemoryContainerRepository()
        biz = CollectionBusinessService(cards_repo, copies_repo, containers_repo)
        moment = self._moment()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        first = CollectionCard.create(
            DomainId("11111111-1111-4111-8111-111111111101"),
            "One",
            metadata,
            external_id="SKU-DUP",
        )
        second = CollectionCard.create(
            DomainId("22222222-2222-4222-8222-222222222202"),
            "Two",
            metadata,
            external_id="sku-dup",
        )
        cards_repo.save(first)
        cards_repo.save(second)
        dups = biz.find_duplicate_catalog_cards_by_external_id()
        assert len(dups) == 1
        assert dups[0].external_id_key == "sku-dup"
        assert len(dups[0].cards) == 2

    def test_duplicate_copy_signatures_active_only(self) -> None:
        """Doublons de signature sur copies en inventaire uniquement."""
        biz, cards, copies_s, _ = self._services()
        t0 = self._moment()
        card = cards.create_card("Same", t0)
        owner = DomainId("eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee")
        copies_s.create_copy(
            card.entity_id,
            owner,
            t0,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
            language="fr",
            finish="holo",
        )
        copies_s.create_copy(
            card.entity_id,
            owner,
            t0 + timedelta(seconds=1),
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
            language="fr",
            finish="holo",
        )
        groups = biz.find_duplicate_active_copy_signatures()
        assert len(groups) == 1
        assert len(groups[0].copies) == 2
