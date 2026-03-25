"""Types légers exposés par les services métier de collection (read models)."""

from __future__ import annotations

from dataclasses import dataclass

from baobab_collection_core.domain.collection_card import CollectionCard
from baobab_collection_core.domain.container import Container
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.physical_copy import PhysicalCopy


@dataclass(frozen=True, slots=True)
class CopyLocation:
    """Emplacement résolu d'une copie physique pour affichage ou API.

    :ivar copy_id: Identifiant de l'exemplaire.
    :ivar card_id: Carte de référence.
    :ivar container_id: Contenant courant, le cas échéant.
    :ivar container_name: Libellé du contenant si résolu en base, sinon ``None``.
    :ivar location_note: Note d'emplacement libre sur la copie.
    """

    copy_id: DomainId
    card_id: DomainId
    container_id: DomainId | None
    container_name: str | None
    location_note: str | None


@dataclass(frozen=True, slots=True)
class ContainerInventoryView:
    """Contenu listable d'un contenant (enfants + exemplaires actifs)."""

    container_id: DomainId
    child_containers: tuple[Container, ...]
    physical_copies: tuple[PhysicalCopy, ...]


@dataclass(frozen=True, slots=True)
class DuplicateCatalogCardGroup:
    """Plusieurs références carte partagent le même identifiant externe normalisé."""

    external_id_key: str
    cards: tuple[CollectionCard, ...]


@dataclass(frozen=True, slots=True)
class DuplicateCopySignatureGroup:
    """Exemplaires actifs partageant la même signature (carte, propriétaire, langue, finition)."""

    card_id: DomainId
    owner_user_id: DomainId
    language: str | None
    finish: str | None
    copies: tuple[PhysicalCopy, ...]
