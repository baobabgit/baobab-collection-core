"""Tests pour :class:`SyncSessionOutcome`."""

from baobab_collection_core.domain.sync_session_outcome import SyncSessionOutcome


class TestSyncSessionOutcome:
    """Quatre statuts attendus par la spec feature 09."""

    def test_four_statuses(self) -> None:
        """synced, pending, conflict, sync_error."""
        assert SyncSessionOutcome.SYNCED.value == "synced"
        assert SyncSessionOutcome.PENDING.value == "pending"
        assert SyncSessionOutcome.CONFLICT.value == "conflict"
        assert SyncSessionOutcome.SYNC_ERROR.value == "sync_error"
