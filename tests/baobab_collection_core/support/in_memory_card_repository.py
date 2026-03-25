"""Implémentation mémoire de :class:`CardRepositoryPort` pour les tests."""

from __future__ import annotations

from collections.abc import Sequence

from baobab_collection_core.domain.collection_card import CollectionCard
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.ports.card_repository_port import CardRepositoryPort


class InMemoryCardRepository(CardRepositoryPort):
    """Stockage volatile des cartes."""

    __slots__ = ("_storage",)

    def __init__(self) -> None:
        self._storage: dict[str, CollectionCard] = {}

    def get_by_id(self, card_id: DomainId) -> CollectionCard | None:
        """Voir :meth:`CardRepositoryPort.get_by_id`."""
        return self._storage.get(card_id.value)

    def list_cards(self) -> Sequence[CollectionCard]:
        """Tri déterministe par identifiant."""
        return tuple(sorted(self._storage.values(), key=lambda card: card.entity_id.value))

    def save(self, card: CollectionCard) -> None:
        """Upsert simple."""
        self._storage[card.entity_id.value] = card

    def exists_duplicate_external_id(
        self,
        external_id: str,
        *,
        exclude_card_id: DomainId | None = None,
    ) -> bool:
        """Détecte les doublons via :meth:`CollectionCard.normalize_external_id_key`."""
        target = CollectionCard.normalize_external_id_key(external_id)
        if target is None:
            return False
        exclude = exclude_card_id.value if exclude_card_id is not None else None
        for uid, existing in self._storage.items():
            if exclude is not None and uid == exclude:
                continue
            other = CollectionCard.normalize_external_id_key(existing.external_id)
            if other is not None and other == target:
                return True
        return False
