"""Tests pour :class:`SyncDeltaKind`."""

from baobab_collection_core.domain.sync_delta_kind import SyncDeltaKind


class TestSyncDeltaKind:
    """Couverture minimale."""

    def test_values(self) -> None:
        """Valeurs persistables."""
        assert SyncDeltaKind("push") is SyncDeltaKind.PUSH
