"""Règles explicites de comptage et de disponibilité pour l'inventaire de collection.

Ces fonctions sont pures (sans effet de bord) pour faciliter les tests et la réutilisation
par CLI, UI ou API.

**Copie dans l'inventaire** : non supprimée logiquement (``deleted_at`` absent).
Les copies supprimées logiquement sont **exclues** de tous les agrégats d'inventaire
(distinction, totaux, disponibilités, contenu de contenant, localisation).

**Copie disponible** : copie dans l'inventaire dont le statut métier est ``ACTIVE`` ou
``FOR_TRADE``. Les statuts ``ON_LOAN``, ``ARCHIVED`` et ``LOST`` sont traités comme
**indisponibles** pour la disponibilité immédiate.

**Cartes distinctes (.collection)**: nombre de ``card_id`` **distincts** apparaissant sur au
moins une copie **dans l'inventaire** — ne confond pas avec le nombre de références dans
le catalogue (:class:`~baobab_collection_core.domain.collection_card.CollectionCard`).
"""

from __future__ import annotations

from baobab_collection_core.domain.physical_copy import PhysicalCopy
from baobab_collection_core.domain.physical_copy_business_status import PhysicalCopyBusinessStatus


def is_copy_in_inventory(copy: PhysicalCopy) -> bool:
    """Vrai si la copie participe à l'inventaire (hors suppression logique)."""
    return not copy.is_logically_deleted


def is_copy_available(copy: PhysicalCopy) -> bool:
    """Vrai si la copie est dans l'inventaire et considérée comme disponible à l'usage/échange."""
    if not is_copy_in_inventory(copy):
        return False
    return copy.business_status in (
        PhysicalCopyBusinessStatus.ACTIVE,
        PhysicalCopyBusinessStatus.FOR_TRADE,
    )


def iter_inventory_copies(copies: list[PhysicalCopy]) -> list[PhysicalCopy]:
    """Filtre les copies présentes dans l'inventaire."""
    return [c for c in copies if is_copy_in_inventory(c)]


def count_distinct_card_ids_in_inventory(copies: list[PhysicalCopy]) -> int:
    """Nombre de cartes distinctes possédées (via au moins une copie en inventaire)."""
    return len({c.card_id.value for c in copies if is_copy_in_inventory(c)})


def count_inventory_copies(copies: list[PhysicalCopy]) -> int:
    """Nombre total d'exemplaires en inventaire (non supprimés logiquement)."""
    return sum(1 for c in copies if is_copy_in_inventory(c))


def count_available_copies(copies: list[PhysicalCopy]) -> int:
    """Nombre d'exemplaires disponibles (:func:`is_copy_available`)."""
    return sum(1 for c in copies if is_copy_available(c))
