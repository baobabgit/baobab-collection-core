"""Services métier transverses : inventaire, localisation, agrégats et doublons simples."""

from __future__ import annotations

from collections import defaultdict

from baobab_collection_core.application import collection_counting_rules
from baobab_collection_core.application.collection_business_types import (
    ContainerInventoryView,
    CopyLocation,
    DuplicateCatalogCardGroup,
    DuplicateCopySignatureGroup,
)
from baobab_collection_core.domain.collection_card import CollectionCard
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.physical_copy import PhysicalCopy
from baobab_collection_core.exceptions.card_not_found_exception import CardNotFoundException
from baobab_collection_core.exceptions.container_not_found_exception import (
    ContainerNotFoundException,
)
from baobab_collection_core.exceptions.physical_copy_not_found_exception import (
    PhysicalCopyNotFoundException,
)
from baobab_collection_core.ports.card_repository_port import CardRepositoryPort
from baobab_collection_core.ports.container_repository_port import ContainerRepositoryPort
from baobab_collection_core.ports.physical_copy_repository_port import PhysicalCopyRepositoryPort


class CollectionBusinessService:
    """Indicateurs et vues de lecture sur cartes, copies et contenants.

    Les règles de comptage (inventaire vs disponibilité, exclusions) sont documentées dans
    :mod:`baobab_collection_core.application.collection_counting_rules`.

    :param cards: Référentiel des cartes catalogue.
    :param copies: Référentiel des exemplaires physiques.
    :param containers: Référentiel des contenants.
    """

    __slots__ = ("_cards", "_containers", "_copies")

    def __init__(
        self,
        cards: CardRepositoryPort,
        copies: PhysicalCopyRepositoryPort,
        containers: ContainerRepositoryPort,
    ) -> None:
        self._cards = cards
        self._copies = copies
        self._containers = containers

    def count_distinct_cards_in_collection(self) -> int:
        """Nombre de cartes distinctes possédées (au moins une copie en inventaire)."""
        return collection_counting_rules.count_distinct_card_ids_in_inventory(
            list(self._copies.list_all_physical_copies())
        )

    def count_total_copies_in_inventory(self) -> int:
        """Nombre total d'exemplaires en inventaire (hors suppression logique)."""
        return collection_counting_rules.count_inventory_copies(
            list(self._copies.list_all_physical_copies())
        )

    def count_available_copies(self) -> int:
        """Nombre d'exemplaires disponibles (:mod:`collection_counting_rules`)."""
        return collection_counting_rules.count_available_copies(
            list(self._copies.list_all_physical_copies())
        )

    def get_copy_location(self, copy_id: DomainId) -> CopyLocation:
        """Résout l'emplacement d'une copie en inventaire (contenant + note libre).

        :raises PhysicalCopyNotFoundException: si l'exemplaire est absent ou supprimé logiquement.
        """
        physical_copy = self._copies.get_by_id(copy_id)
        if physical_copy is None or not collection_counting_rules.is_copy_in_inventory(
            physical_copy
        ):
            raise PhysicalCopyNotFoundException(
                "Aucune copie active ne correspond à l'identifiant fourni pour la localisation."
            )
        container_name: str | None = None
        cid = physical_copy.container_id
        if cid is not None:
            container = self._containers.get_by_id(cid)
            if container is not None:
                container_name = container.name
        return CopyLocation(
            copy_id=physical_copy.entity_id,
            card_id=physical_copy.card_id,
            container_id=cid,
            container_name=container_name,
            location_note=physical_copy.location_note,
        )

    def list_active_copies_for_card(self, card_id: DomainId) -> tuple[PhysicalCopy, ...]:
        """Toutes les copies **en inventaire** pour une carte catalogue existante.

        :raises CardNotFoundException: si la carte n'existe pas dans le référentiel.
        """
        if self._cards.get_by_id(card_id) is None:
            raise CardNotFoundException(
                "Aucune carte ne correspond à l'identifiant fourni pour l'inventaire."
            )
        raw = self._copies.list_by_card_id(card_id)
        active = [c for c in raw if collection_counting_rules.is_copy_in_inventory(c)]
        return tuple(sorted(active, key=lambda c: c.entity_id.value))

    def list_container_contents(self, container_id: DomainId) -> ContainerInventoryView:
        """Liste les enfants directs et ce contenant, et les copies **actives** rangées dedans.

        Les copies supprimées logiquement sont exclues du résultat (hors inventaire).

        :raises ContainerNotFoundException: si le contenant est inconnu.
        """
        if self._containers.get_by_id(container_id) is None:
            raise ContainerNotFoundException(
                "Aucun contenant ne correspond à l'identifiant fourni pour le détail."
            )
        children = self._containers.list_direct_children(container_id)
        stored = self._copies.list_by_container_id(container_id)
        in_box = tuple(
            sorted(
                (c for c in stored if collection_counting_rules.is_copy_in_inventory(c)),
                key=lambda c: c.entity_id.value,
            )
        )
        return ContainerInventoryView(
            container_id=container_id,
            child_containers=tuple(children),
            physical_copies=in_box,
        )

    def find_duplicate_catalog_cards_by_external_id(self) -> tuple[DuplicateCatalogCardGroup, ...]:
        """Cartes catalogue partageant un même ``external_id`` normalisé (au moins deux entrées)."""
        buckets: dict[str, list[CollectionCard]] = defaultdict(list)
        for card in self._cards.list_cards():
            key = CollectionCard.normalize_external_id_key(card.external_id)
            if key is None:
                continue
            buckets[key].append(card)
        groups: list[DuplicateCatalogCardGroup] = [
            DuplicateCatalogCardGroup(
                external_id_key=key, cards=tuple(sorted(cards, key=lambda c: c.entity_id.value))
            )
            for key, cards in buckets.items()
            if len(cards) >= 2
        ]
        return tuple(sorted(groups, key=lambda g: g.external_id_key))

    def find_duplicate_active_copy_signatures(self) -> tuple[DuplicateCopySignatureGroup, ...]:
        """Groupes d'au moins deux copies **en inventaire** avec même signature simple.

        Signature : ``(card_id, owner_user_id, language, finish)`` — utile pour signaler des
        entrées potentiellement redondantes sans politique de fusion automatique.
        """
        buckets: dict[tuple[str, str, str | None, str | None], list[PhysicalCopy]] = defaultdict(
            list
        )
        for physical_copy in self._copies.list_all_physical_copies():
            if not collection_counting_rules.is_copy_in_inventory(physical_copy):
                continue
            sig = (
                physical_copy.card_id.value,
                physical_copy.owner_user_id.value,
                physical_copy.language,
                physical_copy.finish,
            )
            buckets[sig].append(physical_copy)
        groups: list[DuplicateCopySignatureGroup] = []
        for copies in buckets.values():
            if len(copies) < 2:
                continue
            ordered = tuple(sorted(copies, key=lambda c: c.entity_id.value))
            first = ordered[0]
            groups.append(
                DuplicateCopySignatureGroup(
                    card_id=first.card_id,
                    owner_user_id=first.owner_user_id,
                    language=first.language,
                    finish=first.finish,
                    copies=ordered,
                )
            )
        return tuple(
            sorted(
                groups,
                key=lambda g: (
                    g.card_id.value,
                    g.owner_user_id.value,
                    g.language or "",
                    g.finish or "",
                ),
            )
        )
