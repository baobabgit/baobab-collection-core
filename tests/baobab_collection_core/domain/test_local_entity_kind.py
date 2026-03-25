"""Tests pour :class:`LocalEntityKind`."""

from baobab_collection_core.domain.local_entity_kind import LocalEntityKind


class TestLocalEntityKind:
    """Valeurs stables pour persistance."""

    def test_round_trip(self) -> None:
        """StrEnum reconstruit depuis la valeur."""
        assert LocalEntityKind("physical_copy") is LocalEntityKind.PHYSICAL_COPY
