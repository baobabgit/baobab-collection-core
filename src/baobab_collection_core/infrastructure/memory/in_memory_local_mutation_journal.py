"""Adaptateur mémoire pour le journal des mutations locales."""

from __future__ import annotations

from collections.abc import Sequence

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_mutation import LocalMutation
from baobab_collection_core.exceptions.mutation_not_found_exception import MutationNotFoundException
from baobab_collection_core.exceptions.validation_exception import ValidationException
from baobab_collection_core.ports.local_mutation_journal_port import LocalMutationJournalPort


class InMemoryLocalMutationJournal(LocalMutationJournalPort):
    """Journal append-mostly avec remplacement contrôlé pour accusés de synchro."""

    __slots__ = ("_storage",)

    def __init__(self) -> None:
        self._storage: dict[str, LocalMutation] = {}

    def append(self, mutation: LocalMutation) -> None:
        """Refuse les doublons d'identifiant (cohérence append-only)."""
        key = mutation.mutation_id.value
        if key in self._storage:
            raise ValidationException(
                "Identifiant de mutation déjà présent dans le journal mémoire."
            )
        self._storage[key] = mutation

    def get_by_id(self, mutation_id: DomainId) -> LocalMutation | None:
        """Voir :meth:`LocalMutationJournalPort.get_by_id`."""
        return self._storage.get(mutation_id.value)

    def list_pending(self) -> Sequence[LocalMutation]:
        """Entrées ``is_pending`` triées par instant puis identifiant."""
        return tuple(
            sorted(
                (m for m in self._storage.values() if m.is_pending),
                key=lambda item: (item.recorded_at, item.mutation_id.value),
            )
        )

    def replace(self, mutation: LocalMutation) -> None:
        """Exige une entrée existante du même ``mutation_id``."""
        key = mutation.mutation_id.value
        if key not in self._storage:
            raise MutationNotFoundException(
                "Impossible de remplacer une mutation absente du journal."
            )
        self._storage[key] = mutation
