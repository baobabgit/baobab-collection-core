"""Action prévue dans un plan de synchronisation."""

from enum import StrEnum


class SyncPlanAction(StrEnum):
    """Instruction pour un adaptateur de transport ou une tâche locale.

    :cvar NO_OP: Aucune opération I/O attendue.
    :cvar PUSH: Envoyer les changements locaux.
    :cvar PULL: Récupérer la révision distante.
    :cvar REPORT_CONFLICT: Escalade vers détection / résolution de conflit applicative.
    """

    NO_OP = "no_op"
    PUSH = "push"
    PULL = "pull"
    REPORT_CONFLICT = "report_conflict"
