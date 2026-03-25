"""Tests applicatifs du service carte."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.application.card_application_service import CardApplicationService
from baobab_collection_core.domain.collection_card import UNSET
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.exceptions import (
    CardNotFoundException,
    DuplicateCardException,
    InvalidCardException,
)
from tests.baobab_collection_core.support.in_memory_card_repository import InMemoryCardRepository


class TestCardApplicationService:
    """Scénarios CRUD léger sur les références carte."""

    @staticmethod
    def _moment() -> datetime:
        return datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)

    def _svc(self) -> tuple[CardApplicationService, InMemoryCardRepository]:
        repo = InMemoryCardRepository()
        return CardApplicationService(repo), repo

    def test_create_nominal(self) -> None:
        """Création complète avec normalisation d'identifiant externe."""
        svc, _ = self._svc()
        card = svc.create_card(
            "Phoenix",
            self._moment(),
            external_id=" ext-1 ",
            edition="Core",
            tags=("feu",),
        )
        assert card.metadata.sync_state.value == "dirty"
        assert card.external_id == "ext-1"

    def test_create_invalid_name(self) -> None:
        """Les validations domaine remontent jusqu'au service."""
        svc, _ = self._svc()
        with pytest.raises(InvalidCardException):
            svc.create_card("   ", self._moment())

    def test_duplicate_external_id_on_create(self) -> None:
        """Deux cartes ne partagent pas le même identifiant externe."""
        svc, _ = self._svc()
        svc.create_card("A", self._moment(), external_id="dup")
        with pytest.raises(DuplicateCardException):
            svc.create_card("B", self._moment(), external_id="DUP")

    def test_get_not_found(self) -> None:
        """Erreur explicite si la carte n'existe pas."""
        svc, _ = self._svc()
        missing = DomainId("00000000-0000-4000-8000-00000000dead")
        with pytest.raises(CardNotFoundException):
            svc.get_card_by_id(missing)

    def test_update_and_list(self) -> None:
        """Mise à jour persistée et vue liste."""
        svc, _ = self._svc()
        first = svc.create_card("One", self._moment())
        svc.create_card("Two", self._moment() + timedelta(seconds=1))
        svc.update_card(
            first.entity_id,
            self._moment() + timedelta(minutes=5),
            name="One renamed",
            tags=("x",),
        )
        cards = svc.list_cards()
        assert len(cards) == 2
        refreshed = svc.get_card_by_id(first.entity_id)
        assert refreshed.name == "One renamed"
        assert refreshed.tags == ("x",)

    def test_update_duplicate_external(self) -> None:
        """Collision détectée lors du renommage d'identifiant."""
        svc, _ = self._svc()
        svc.create_card("A", self._moment(), external_id="id-a")
        second = svc.create_card(
            "B",
            self._moment() + timedelta(seconds=1),
            external_id="id-b",
        )
        with pytest.raises(DuplicateCardException):
            svc.update_card(
                second.entity_id,
                self._moment() + timedelta(minutes=1),
                external_id="ID-A",
            )

    def test_partial_update_preserves_unset_fields(self) -> None:
        """Omettre un champ ou passer ``UNSET`` évite d'écraser la valeur."""
        svc, _ = self._svc()
        card = svc.create_card("Keep", self._moment(), language="fr")
        svc.update_card(
            card.entity_id,
            self._moment() + timedelta(minutes=2),
            edition="Promo",
            language=UNSET,
        )
        refreshed = svc.get_card_by_id(card.entity_id)
        assert refreshed.language == "fr"
        assert refreshed.edition == "Promo"
