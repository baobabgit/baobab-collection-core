"""Nature fonctionnelle d'une mutation enregistrée localement."""

from enum import StrEnum


class LocalMutationKind(StrEnum):
    """Opération traçable pour la synchro ultérieure (hors transport).

    :cvar CREATE: Création locale de l'entité cible.
    :cvar UPDATE: Mise à jour de champs ou d'état hors déplacement structurel majeur.
    :cvar SOFT_DELETE: Suppression logique à propager.
    :cvar MOVE: Changement de parent / hiérarchie (contenant, arborescence).
    :cvar ATTACH: Rattachement explicite (ex. copie vers contenant).
    :cvar DETACH: Détachement explicite.
    """

    CREATE = "create"
    UPDATE = "update"
    SOFT_DELETE = "soft_delete"
    MOVE = "move"
    ATTACH = "attach"
    DETACH = "detach"
