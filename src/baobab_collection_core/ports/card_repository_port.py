"""Contrat de persistance pour l'entité :class:`CollectionCard`."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from baobab_collection_core.domain.collection_card import CollectionCard
from baobab_collection_core.domain.domain_id import DomainId


class CardRepositoryPort(ABC):
    """Port hexagonal pour les références carte sans technologie de stockage imposée."""

    @abstractmethod
    def get_by_id(self, card_id: DomainId) -> CollectionCard | None:
        """Retourne la carte ou ``None`` si elle est absente."""

    @abstractmethod
    def list_cards(self) -> Sequence[CollectionCard]:
        """Liste les cartes (ordre laissé à l'implémentation)."""

    @abstractmethod
    def save(self, card: CollectionCard) -> None:
        """Crée ou met à jour la carte fournie."""

    @abstractmethod
    def exists_duplicate_external_id(
        self,
        external_id: str,
        *,
        exclude_card_id: DomainId | None = None,
    ) -> bool:
        """Indique si un autre enregistrement possède le même identifiant externe.

        :param external_id: Valeur non vide (déjà normalisée côté appelant).
        :param exclude_card_id: Permet d'exclure la carte en cours de mise à jour.
        :returns: ``True`` si un conflit existe (comparaison ``casefold`` recommandée).
        """
