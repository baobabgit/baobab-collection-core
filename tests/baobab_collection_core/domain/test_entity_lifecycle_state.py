"""Tests pour :class:`EntityLifecycleState`."""

from baobab_collection_core.domain.entity_lifecycle_state import EntityLifecycleState


class TestEntityLifecycleState:
    """Statuts de cycle de vie orthogonaux à la synchro."""

    def test_values(self) -> None:
        """Valeurs string stables."""
        assert EntityLifecycleState.DRAFT.value == "draft"
        assert EntityLifecycleState.ACTIVE.value == "active"
        assert EntityLifecycleState.ARCHIVED.value == "archived"
