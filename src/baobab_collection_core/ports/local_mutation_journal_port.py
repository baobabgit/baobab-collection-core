"""Contrat de persistance du journal des mutations locales."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_mutation import LocalMutation


class LocalMutationJournalPort(ABC):
    """Journal append-mostly ; mise à jour limitée pour accusés de synchro locaux."""

    @abstractmethod
    def append(self, mutation: LocalMutation) -> None:
        """Ajoute une entrée (identifiant unique attendu)."""

    @abstractmethod
    def get_by_id(self, mutation_id: DomainId) -> LocalMutation | None:
        """Retourne l'entrée ou ``None``."""

    @abstractmethod
    def list_pending(self) -> Sequence[LocalMutation]:
        """Entrées encore en attente de propagation, ordre déterministe laissé au port."""

    @abstractmethod
    def replace(self, mutation: LocalMutation) -> None:
        """Remplace une entrée existante (même ``mutation_id``)."""
