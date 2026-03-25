"""Classification des contenants de rangement."""

from enum import StrEnum


class ContainerKind(StrEnum):
    """Type de contenant extensible côté persistance (valeurs stables).

    :cvar BOX: Boîte de stockage.
    :cvar BINDER: Classeur.
    :cvar DECK_BOX: Deck box.
    :cvar STACK: Pile.
    :cvar TEMP_ZONE: Zone temporaire.
    :cvar LOGICAL_GROUP: Regroupement logique.
    """

    BOX = "box"
    BINDER = "binder"
    DECK_BOX = "deck_box"
    STACK = "stack"
    TEMP_ZONE = "temp_zone"
    LOGICAL_GROUP = "logical_group"
