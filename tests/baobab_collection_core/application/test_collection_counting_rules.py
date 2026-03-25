"""Tests des règles pures de comptage d'inventaire."""

from datetime import datetime, timezone

from baobab_collection_core.application.collection_counting_rules import (
    count_available_copies,
    count_distinct_card_ids_in_inventory,
    count_inventory_copies,
    is_copy_available,
    is_copy_in_inventory,
    iter_inventory_copies,
)
from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.physical_copy import PhysicalCopy
from baobab_collection_core.domain.physical_copy_business_status import PhysicalCopyBusinessStatus
from baobab_collection_core.domain.physical_copy_condition import PhysicalCopyCondition
from baobab_collection_core.domain.sync_state import SyncState


class TestCollectionCountingRules:
    """Cas nominaux et limites sans référentiel."""

    @staticmethod
    def _moment() -> datetime:
        return datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)

    @staticmethod
    def _owner() -> DomainId:
        return DomainId("11111111-1111-4111-8111-111111111111")

    def _copy(
        self,
        *,
        copy_id: str,
        card_id: str,
        deleted: bool = False,
        status: PhysicalCopyBusinessStatus = PhysicalCopyBusinessStatus.ACTIVE,
    ) -> PhysicalCopy:
        moment = self._moment()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        meta = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        if deleted:
            meta = meta.mark_deleted(moment)
        return PhysicalCopy.create(
            DomainId(copy_id),
            DomainId(card_id),
            self._owner(),
            meta,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=status,
        )

    def test_deleted_excluded_from_inventory(self) -> None:
        """Suppression logique : hors inventaire."""
        active = self._copy(
            copy_id="10000000-0000-4000-8000-000000000001",
            card_id="20000000-0000-4000-8000-000000000001",
        )
        gone = self._copy(
            copy_id="10000000-0000-4000-8000-000000000002",
            card_id="20000000-0000-4000-8000-000000000002",
            deleted=True,
        )
        assert is_copy_in_inventory(active) is True
        assert is_copy_in_inventory(gone) is False
        assert count_inventory_copies([active, gone]) == 1
        assert count_distinct_card_ids_in_inventory([active, gone]) == 1

    def test_available_only_active_and_for_trade(self) -> None:
        """Disponibilité : ACTIVE et FOR_TRADE uniquement parmi l'inventaire."""
        loan = self._copy(
            copy_id="10000000-0000-4000-8000-000000000011",
            card_id="20000000-0000-4000-8000-000000000011",
            status=PhysicalCopyBusinessStatus.ON_LOAN,
        )
        lost = self._copy(
            copy_id="10000000-0000-4000-8000-000000000012",
            card_id="20000000-0000-4000-8000-000000000012",
            status=PhysicalCopyBusinessStatus.LOST,
        )
        trade = self._copy(
            copy_id="10000000-0000-4000-8000-000000000013",
            card_id="20000000-0000-4000-8000-000000000013",
            status=PhysicalCopyBusinessStatus.FOR_TRADE,
        )
        assert is_copy_available(loan) is False
        assert is_copy_available(lost) is False
        assert is_copy_available(trade) is True
        assert count_available_copies([loan, lost, trade]) == 1

    def test_distinct_cards_counts_card_ids(self) -> None:
        """Cartes distinctes = cardinal des card_id en inventaire."""
        cid_a = "20000000-0000-4000-8000-0000000000aa"
        cid_b = "20000000-0000-4000-8000-0000000000bb"
        c1 = self._copy(copy_id="10000000-0000-4000-8000-0000000000a1", card_id=cid_a)
        c2 = self._copy(copy_id="10000000-0000-4000-8000-0000000000a2", card_id=cid_b)
        c3 = PhysicalCopy.create(
            DomainId("10000000-0000-4000-8000-0000000000a3"),
            DomainId(cid_a),
            self._owner(),
            c1.metadata,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
        )
        assert count_distinct_card_ids_in_inventory([c1, c2, c3]) == 2

    def test_iter_inventory_copies_filters_deleted(self) -> None:
        """Itérateur inventaire cohérent avec les comptages."""
        copies = [
            self._copy(
                copy_id=f"10000000-0000-4000-8000-{i:012d}",
                card_id=f"20000000-0000-4000-8000-{i:012d}",
            )
            for i in (101, 102, 103)
        ]
        copies.append(
            self._copy(
                copy_id="10000000-0000-4000-8000-000000000199",
                card_id="20000000-0000-4000-8000-000000000199",
                deleted=True,
            )
        )
        inv = iter_inventory_copies(copies)
        assert len(inv) == 3
