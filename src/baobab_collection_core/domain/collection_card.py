"""Entité métier : carte de collection (référence), distincte d'une copie physique."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any, Final

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_base import EntityBase
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.invalid_card_exception import InvalidCardException

UNSET: Final[Any] = object()

_MAX_NAME_LEN = 256
_MAX_EXTERNAL_ID_LEN = 128
_MAX_EDITION_LEN = 128
_MAX_CATALOG_VERSION_LEN = 64
_MAX_LANGUAGE_LEN = 32
_MAX_TAG_LEN = 64
_MAX_TAGS = 48


class CollectionCard(EntityBase):
    """Référence de collection pour une carte (agrégat sans exemplaire physique).

    L'``entity_id`` est l'identifiant stable qui pourra lier plusieurs exemplaires physiques
    dans une future feature : il sert de racine d'agrégat métier, indépendamment des SKU.

    :param entity_id: Identifiant interne immuable.
    :param name: Nom de la carte (obligatoire).
    :param metadata: Audit, version optimiste et synchronisation.
    :param external_id: Référence externe optionnelle (catalogue, import).
    :param edition: Édition optionnelle (booster, set, etc.).
    :param catalog_version: Libellé de version métier optionnel (hors :class:`EntityVersion`).
    :param language: Code ou libellé de langue optionnel.
    :param tags: Étiquettes de classement immuables.

    :ivar _name: Nom affiché métier.
    :ivar _external_id: Identifiant externe normalisé ou ``None``.
    :ivar _edition: Édition ou ``None``.
    :ivar _catalog_version: Version catalogue ou ``None``.
    :ivar _language: Langue ou ``None``.
    :ivar _tags: Tags normalisés.
    """

    __slots__ = (
        "_name",
        "_external_id",
        "_edition",
        "_catalog_version",
        "_language",
        "_tags",
    )

    def __init__(
        self,
        entity_id: DomainId,
        name: str,
        metadata: EntityMetadata,
        *,
        external_id: str | None = None,
        edition: str | None = None,
        catalog_version: str | None = None,
        language: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> None:
        super().__init__(entity_id, metadata)
        self._name = CollectionCard._validate_name(name)
        self._external_id = CollectionCard._validate_optional_short_text(
            external_id, "external_id", _MAX_EXTERNAL_ID_LEN
        )
        self._edition = CollectionCard._validate_optional_short_text(
            edition, "edition", _MAX_EDITION_LEN
        )
        self._catalog_version = CollectionCard._validate_optional_short_text(
            catalog_version, "catalog_version", _MAX_CATALOG_VERSION_LEN
        )
        self._language = CollectionCard._validate_optional_short_text(
            language, "language", _MAX_LANGUAGE_LEN
        )
        self._tags = CollectionCard._validate_tags(tags)

    @property
    def name(self) -> str:
        """Nom de la carte."""
        return self._name

    @property
    def external_id(self) -> str | None:
        """Identifiant externe optionnel."""
        return self._external_id

    @property
    def edition(self) -> str | None:
        """Édition optionnelle."""
        return self._edition

    @property
    def catalog_version(self) -> str | None:
        """Libellé de version de set optionnel (non confondu avec la version d'entité)."""
        return self._catalog_version

    @property
    def language(self) -> str | None:
        """Langue optionnelle."""
        return self._language

    @property
    def tags(self) -> tuple[str, ...]:
        """Tags immuables."""
        return self._tags

    @classmethod
    def create(
        cls,
        entity_id: DomainId,
        name: str,
        metadata: EntityMetadata,
        *,
        external_id: str | None = None,
        edition: str | None = None,
        catalog_version: str | None = None,
        language: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> CollectionCard:
        """Fabrique une carte cohérente avec ses métadonnées initiales."""
        return cls(
            entity_id,
            name,
            metadata,
            external_id=external_id,
            edition=edition,
            catalog_version=catalog_version,
            language=language,
            tags=tags,
        )

    @classmethod
    def sanitize_external_id(cls, value: str | None) -> str | None:
        """Valide et normalise un identifiant externe pour persistance ou contrôle de doublon.

        :param value: Texte brut ou ``None``.
        :returns: Chaîne non vide stripped ou ``None``.
        """
        return cls._validate_optional_short_text(
            value,
            "external_id",
            _MAX_EXTERNAL_ID_LEN,
        )

    @staticmethod
    def normalize_external_id_key(external_id: str | None) -> str | None:
        """Clé insensible à la casse pour détecter les doublons d'identifiant externe."""
        prepared = CollectionCard.sanitize_external_id(external_id)
        if prepared is None:
            return None
        return prepared.casefold()

    def update_reference_data(  # pylint: disable=too-many-locals
        self,
        moment: datetime,
        *,
        name: str | Any = UNSET,
        external_id: str | None | Any = UNSET,
        edition: str | None | Any = UNSET,
        catalog_version: str | None | Any = UNSET,
        language: str | None | Any = UNSET,
        tags: tuple[str, ...] | Any = UNSET,
    ) -> None:
        """Met à jour les champs éditables ; arguments absents = inchangés.

        Passer ``None`` pour un champ optionnel le vide explicitement après validation.

        :param moment: Instant métier de la modification.
        :raises InvalidCardException: si les nouvelles valeurs sont invalides.
        """
        candidate_name = self._name if name is UNSET else CollectionCard._validate_name(name)
        candidate_external = (
            self._external_id
            if external_id is UNSET
            else CollectionCard._validate_optional_short_text(
                external_id,
                "external_id",
                _MAX_EXTERNAL_ID_LEN,
            )
        )
        candidate_edition = (
            self._edition
            if edition is UNSET
            else CollectionCard._validate_optional_short_text(
                edition,
                "edition",
                _MAX_EDITION_LEN,
            )
        )
        candidate_catalog = (
            self._catalog_version
            if catalog_version is UNSET
            else CollectionCard._validate_optional_short_text(
                catalog_version,
                "catalog_version",
                _MAX_CATALOG_VERSION_LEN,
            )
        )
        candidate_language = (
            self._language
            if language is UNSET
            else CollectionCard._validate_optional_short_text(
                language,
                "language",
                _MAX_LANGUAGE_LEN,
            )
        )
        candidate_tags = self._tags if tags is UNSET else CollectionCard._validate_tags(tags)

        unchanged = (
            candidate_name == self._name
            and candidate_external == self._external_id
            and candidate_edition == self._edition
            and candidate_catalog == self._catalog_version
            and candidate_language == self._language
            and candidate_tags == self._tags
        )
        if unchanged:
            return

        new_meta = self._metadata.bump_version(moment).with_sync_state(SyncState.DIRTY)
        self.replace_metadata(new_meta)
        self._name = candidate_name
        self._external_id = candidate_external
        self._edition = candidate_edition
        self._catalog_version = candidate_catalog
        self._language = candidate_language
        self._tags = candidate_tags

    @staticmethod
    def _validate_name(value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise InvalidCardException("Le nom de la carte ne peut pas être vide.")
        if len(stripped) > _MAX_NAME_LEN:
            raise InvalidCardException(
                f"Le nom de la carte ne peut pas dépasser {_MAX_NAME_LEN} caractères."
            )
        return stripped

    @staticmethod
    def _validate_optional_short_text(
        value: str | None,
        field_label: str,
        max_len: int,
    ) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            return None
        if len(stripped) > max_len:
            raise InvalidCardException(
                f"Le champ {field_label} ne peut pas dépasser {max_len} caractères."
            )
        return stripped

    @staticmethod
    def _validate_tags(tags: Iterable[str]) -> tuple[str, ...]:
        normalized: list[str] = []
        seen: set[str] = set()
        for raw in tags:
            token = raw.strip()
            if not token:
                raise InvalidCardException("Les tags ne peuvent pas contenir de valeur vide.")
            if len(token) > _MAX_TAG_LEN:
                raise InvalidCardException(
                    f"Un tag ne peut pas dépasser {_MAX_TAG_LEN} caractères."
                )
            key = token.casefold()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(token)
        if len(normalized) > _MAX_TAGS:
            raise InvalidCardException(
                f"Une carte ne peut pas porter plus de {_MAX_TAGS} tags distincts."
            )
        return tuple(normalized)
