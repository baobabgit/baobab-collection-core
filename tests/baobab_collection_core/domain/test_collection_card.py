"""Tests unitaires pour :class:`CollectionCard`."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.collection_card import UNSET, CollectionCard
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions import InvalidCardException


class TestCollectionCard:
    """Règles métier locales et immuabilité apparente des tags."""

    @staticmethod
    def _now() -> datetime:
        return datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc)

    def _base_card(self) -> CollectionCard:
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        return CollectionCard.create(
            DomainId("00000000-0000-4000-8000-00000000c4d0"),
            "Dragon bleu",
            metadata,
            external_id="SKU-1",
            edition="Première édition",
            catalog_version="v3",
            language="fr",
            tags=("foil", "rare"),
        )

    def test_name_required(self) -> None:
        """Nom vide interdit."""
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        with pytest.raises(InvalidCardException):
            CollectionCard.create(
                DomainId("00000000-0000-4000-8000-00000000c0de"),
                "  ",
                metadata,
            )

    def test_update_bumps_version_and_dirty(self) -> None:
        """Mutation métier synchronisée avec EntityMetadata."""
        card = self._base_card()
        later = card.metadata.timestamps.updated_at + timedelta(minutes=10)
        card.update_reference_data(later, name="Dragon bleu alpha")
        assert card.name == "Dragon bleu alpha"
        assert card.metadata.version.value == 1
        assert card.metadata.sync_state.value == "dirty"

    def test_update_no_op_keeps_version(self) -> None:
        """Aucun changement effectif : pas d'incrément parasite."""
        card = self._base_card()
        version_before = card.metadata.version.value
        card.update_reference_data(card.metadata.timestamps.updated_at + timedelta(seconds=5))
        assert card.metadata.version.value == version_before

    def test_clear_optional_fields_with_none(self) -> None:
        """None explicite vide les attributs optionnels."""
        card = self._base_card()
        moment = card.metadata.timestamps.updated_at + timedelta(hours=1)
        card.update_reference_data(
            moment,
            external_id=None,
            edition=None,
            catalog_version=None,
            language=None,
            tags=(),
        )
        assert card.external_id is None
        assert card.edition is None
        assert card.catalog_version is None
        assert card.language is None
        assert card.tags == ()

    def test_tags_reject_empty_token(self) -> None:
        """Tag vide interdit."""
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        with pytest.raises(InvalidCardException):
            CollectionCard.create(
                DomainId("00000000-0000-4000-8000-00000000b4d0"),
                "Carte",
                metadata,
                tags=("ok", "  "),
            )

    def test_unset_leaves_fields_intact(self) -> None:
        """La sentinelle UNSET laisse les champs inchangés lors d'un patch partiel."""
        card = self._base_card()
        before_tags = card.tags
        before_name = card.name
        moment = card.metadata.timestamps.updated_at + timedelta(minutes=2)
        card.update_reference_data(moment, language="en", name=UNSET, tags=UNSET)
        assert card.tags == before_tags
        assert card.name == before_name
        assert card.language == "en"

    def test_normalize_external_id_key(self) -> None:
        """Clé de doublon basée sur strip + casefold."""
        assert CollectionCard.normalize_external_id_key(" Ref-ABC ") == "ref-abc"
        assert CollectionCard.normalize_external_id_key(None) is None

    def test_name_length_guard(self) -> None:
        """Garde-fou sur la longueur du nom."""
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        long_name = "x" * 257
        with pytest.raises(InvalidCardException):
            CollectionCard.create(
                DomainId("11111111-1111-4111-8111-111111111111"),
                long_name,
                metadata,
            )

    def test_optional_field_blank_resets_to_none(self) -> None:
        """Une chaîne uniquement blanche normalise en valeur absente."""
        card = self._base_card()
        moment = card.metadata.timestamps.updated_at + timedelta(minutes=3)
        card.update_reference_data(moment, edition="    ")
        assert card.edition is None

    def test_optional_field_too_long_rejected(self) -> None:
        """Les limites de taille s'appliquent aussi en mise à jour."""
        card = self._base_card()
        moment = card.metadata.timestamps.updated_at + timedelta(minutes=4)
        too_long_external = "x" * 129
        with pytest.raises(InvalidCardException):
            card.update_reference_data(moment, external_id=too_long_external)
