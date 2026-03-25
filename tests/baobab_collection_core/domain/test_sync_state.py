"""Tests pour :class:`SyncState`."""

from baobab_collection_core.domain.sync_state import SyncState


class TestSyncState:
    """Valeurs stables pour persistance et API."""

    def test_expected_members(self) -> None:
        """Jeu complet attendu par la spécification."""
        assert SyncState.CLEAN.value == "clean"
        assert SyncState.DIRTY.value == "dirty"
        assert SyncState.SYNCED.value == "synced"
        assert SyncState.CONFLICT.value == "conflict"
        assert SyncState.SYNC_ERROR.value == "sync_error"
        assert SyncState.DELETED.value == "deleted"

    def test_round_trip_from_value(self) -> None:
        """StrEnum permet de reconstruire depuis la valeur persistée."""
        assert SyncState("dirty") is SyncState.DIRTY
