"""Tests pour :class:`LocalMutationKind`."""

from baobab_collection_core.domain.local_mutation_kind import LocalMutationKind


class TestLocalMutationKind:
    """Couverture minimale des types de mutation."""

    def test_expected_members(self) -> None:
        """Valeurs principales attendues."""
        assert LocalMutationKind.CREATE.value == "create"
        assert LocalMutationKind.SOFT_DELETE.value == "soft_delete"
        assert LocalMutationKind.ATTACH.value == "attach"
