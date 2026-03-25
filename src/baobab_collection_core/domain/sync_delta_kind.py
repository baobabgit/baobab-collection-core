"""Classification d'écart entre instantanés local et distant."""

from enum import StrEnum


class SyncDeltaKind(StrEnum):
    """Écart calculé lors de la comparaison entre instantanés local et distant.

    :cvar NONE: Rien à faire pour cette entité.
    :cvar PUSH: Propager des changements locaux vers le pair.
    :cvar PULL: Récupérer l'état distant plus récent.
    :cvar CONFLICT: Versions divergentes avec travail local non résolu.
    """

    NONE = "none"
    PUSH = "push"
    PULL = "pull"
    CONFLICT = "conflict"
