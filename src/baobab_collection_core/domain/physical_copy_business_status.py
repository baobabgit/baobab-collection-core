"""Statut métier d'une copie physique dans la collection."""

from enum import StrEnum


class PhysicalCopyBusinessStatus(StrEnum):
    """Position fonctionnelle de l'exemplaire (hors synchronisation transport).

    :cvar ACTIVE: Copie utilisable dans la collection courante.
    :cvar ON_LOAN: Prêtée temporairement.
    :cvar FOR_TRADE: Disponible pour échange ou vente.
    :cvar ARCHIVED: Retirée du flux principal mais conservée.
    :cvar LOST: Considérée comme perdue côté métier.
    """

    ACTIVE = "active"
    ON_LOAN = "on_loan"
    FOR_TRADE = "for_trade"
    ARCHIVED = "archived"
    LOST = "lost"
