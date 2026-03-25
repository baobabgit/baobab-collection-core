"""Décision produite par une stratégie injectable de résolution de conflit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.sync_session_outcome import SyncSessionOutcome

ConflictWinner = Literal["local", "remote", "manual"]


@dataclass(frozen=True, slots=True)
class ConflictResolutionDecision:
    """Résultat purement métier : interprétable par la couche orchestrant la synchro.

    :ivar outcome: Issue logique (voir ``SyncSessionOutcome``).
    :ivar winner: Branche privilégiée si applicable.
    :ivar adopted_version: Version cible suggérée après résolution, si déterministe.
    :ivar adopted_parent_container_id: Parent cible pour réconciliation de contenant.
    :ivar requires_manual_resolution: Vrai si l'UI ou un opérateur doit trancher hors automate.
    :ivar notes: Détail optionnel pour diagnostics.
    """

    outcome: SyncSessionOutcome
    winner: ConflictWinner | None
    adopted_version: int | None
    adopted_parent_container_id: DomainId | None
    requires_manual_resolution: bool
    notes: str | None = None
