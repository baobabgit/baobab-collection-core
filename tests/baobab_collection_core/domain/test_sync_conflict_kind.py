"""Tests pour :class:`SyncConflictKind`."""

from baobab_collection_core.domain.sync_conflict_kind import SyncConflictKind


class TestSyncConflictKind:
    """Couverture minimale."""

    def test_str_enum_roundtrip(self) -> None:
        """Valeurs sérialisables."""
        assert SyncConflictKind("version_divergence") is SyncConflictKind.VERSION_DIVERGENCE
