"""Cas d'usage applicatifs pour les cartes de collection."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.collection_card import UNSET, CollectionCard
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.card_not_found_exception import CardNotFoundException
from baobab_collection_core.exceptions.duplicate_card_exception import DuplicateCardException
from baobab_collection_core.ports.card_repository_port import CardRepositoryPort


class CardApplicationService:
    """Orchestre le cycle de vie des références :class:`CollectionCard`.

    :param cards: Port de persistance injecté.
    """

    __slots__ = ("_cards",)

    def __init__(self, cards: CardRepositoryPort) -> None:
        self._cards = cards

    def create_card(
        self,
        name: str,
        moment: datetime,
        *,
        external_id: str | None = None,
        edition: str | None = None,
        catalog_version: str | None = None,
        language: str | None = None,
        tags: Sequence[str] = (),
    ) -> CollectionCard:
        """Crée une carte avec métadonnées initiales ``DIRTY`` et version ``0``.

        :raises DuplicateCardException: si l'identifiant externe est déjà pris.
        """
        prepared_external = CollectionCard.sanitize_external_id(external_id)
        if prepared_external is not None and self._cards.exists_duplicate_external_id(
            prepared_external,
        ):
            raise DuplicateCardException(
                "Une autre carte possède déjà cet identifiant externe dans la collection."
            )
        entity_id = DomainId(str(uuid.uuid4()))
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.DIRTY,
        )
        card = CollectionCard.create(
            entity_id,
            name,
            metadata,
            external_id=external_id,
            edition=edition,
            catalog_version=catalog_version,
            language=language,
            tags=tuple(tags),
        )
        self._cards.save(card)
        return card

    def update_card(
        self,
        card_id: DomainId,
        moment: datetime,
        *,
        name: str | Any = UNSET,
        external_id: str | None | Any = UNSET,
        edition: str | None | Any = UNSET,
        catalog_version: str | None | Any = UNSET,
        language: str | None | Any = UNSET,
        tags: tuple[str, ...] | Any = UNSET,
    ) -> CollectionCard:
        """Met à jour partiellement les attributs éditables (paramètres omis = inchangés)."""
        card = self._require_card(card_id)
        if external_id is not UNSET:
            prepared = CollectionCard.sanitize_external_id(external_id)
            if prepared is not None and self._cards.exists_duplicate_external_id(
                prepared,
                exclude_card_id=card_id,
            ):
                raise DuplicateCardException(
                    "Une autre carte possède déjà cet identifiant externe dans la collection."
                )
        card.update_reference_data(
            moment,
            name=name,
            external_id=external_id,
            edition=edition,
            catalog_version=catalog_version,
            language=language,
            tags=tags,
        )
        self._cards.save(card)
        return card

    def get_card_by_id(self, card_id: DomainId) -> CollectionCard:
        """Retourne une carte ou lève :class:`CardNotFoundException`."""
        return self._require_card(card_id)

    def list_cards(self) -> list[CollectionCard]:
        """Matérialise la liste fournie par le port."""
        return list(self._cards.list_cards())

    def _require_card(self, card_id: DomainId) -> CollectionCard:
        card = self._cards.get_by_id(card_id)
        if card is None:
            raise CardNotFoundException(
                "Aucune carte ne correspond à l'identifiant fourni dans la collection."
            )
        return card
