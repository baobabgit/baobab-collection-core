"""Statut technique du cycle de vie d'une ressource métier."""

from enum import StrEnum


class EntityLifecycleState(StrEnum):
    """Niveau de maturité ou de visibilité hors synchronisation.

    Orthogonal à :class:`SyncState` : décrit le cycle de vie produit, pas le transport.

    :cvar DRAFT: Brouillon local ou non publié.
    :cvar ACTIVE: Ressource utilisable dans les workflows courants.
    :cvar ARCHIVED: Figée, conservée pour l'historique ou la conformité.
    """

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
