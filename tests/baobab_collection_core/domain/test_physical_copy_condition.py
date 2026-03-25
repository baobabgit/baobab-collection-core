"""Tests pour :class:`PhysicalCopyCondition`."""

from baobab_collection_core.domain.physical_copy_condition import PhysicalCopyCondition


class TestPhysicalCopyCondition:
    """Valeurs stables pour persistance et API."""

    def test_expected_members(self) -> None:
        """Jeu complet attendu."""
        assert PhysicalCopyCondition.MINT.value == "mint"
        assert PhysicalCopyCondition.NEAR_MINT.value == "near_mint"
        assert PhysicalCopyCondition.LIGHT_PLAYED.value == "light_played"
        assert PhysicalCopyCondition.PLAYED.value == "played"
        assert PhysicalCopyCondition.POOR.value == "poor"
        assert PhysicalCopyCondition.UNKNOWN.value == "unknown"

    def test_round_trip_from_value(self) -> None:
        """StrEnum permet de reconstruire depuis la valeur persistée."""
        assert PhysicalCopyCondition("played") is PhysicalCopyCondition.PLAYED
