"""Tests pour :class:`PhysicalCopyBusinessStatus`."""

from baobab_collection_core.domain.physical_copy_business_status import PhysicalCopyBusinessStatus


class TestPhysicalCopyBusinessStatus:
    """Valeurs stables pour persistance et API."""

    def test_expected_members(self) -> None:
        """Jeu complet attendu."""
        assert PhysicalCopyBusinessStatus.ACTIVE.value == "active"
        assert PhysicalCopyBusinessStatus.ON_LOAN.value == "on_loan"
        assert PhysicalCopyBusinessStatus.FOR_TRADE.value == "for_trade"
        assert PhysicalCopyBusinessStatus.ARCHIVED.value == "archived"
        assert PhysicalCopyBusinessStatus.LOST.value == "lost"

    def test_round_trip_from_value(self) -> None:
        """StrEnum permet de reconstruire depuis la valeur persistée."""
        assert PhysicalCopyBusinessStatus("on_loan") is PhysicalCopyBusinessStatus.ON_LOAN
