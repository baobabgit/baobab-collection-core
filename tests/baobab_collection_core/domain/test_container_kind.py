"""Tests pour :class:`ContainerKind`."""

from baobab_collection_core.domain.container_kind import ContainerKind


class TestContainerKind:
    """Valeurs stables pour persistance et API."""

    def test_expected_members(self) -> None:
        """Jeu minimal attendu par la spécification."""
        assert ContainerKind.BOX.value == "box"
        assert ContainerKind.BINDER.value == "binder"
        assert ContainerKind.DECK_BOX.value == "deck_box"
        assert ContainerKind.STACK.value == "stack"
        assert ContainerKind.TEMP_ZONE.value == "temp_zone"
        assert ContainerKind.LOGICAL_GROUP.value == "logical_group"

    def test_round_trip_from_value(self) -> None:
        """StrEnum permet de reconstruire depuis la valeur persistée."""
        assert ContainerKind("binder") is ContainerKind.BINDER
