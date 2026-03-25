"""État matériel observable d'une copie physique."""

from enum import StrEnum


class PhysicalCopyCondition(StrEnum):
    """Gradation simplifiée de l'état de conservation.

    :cvar MINT: Neuf / impeccable.
    :cvar NEAR_MINT: Quasi neuf, défauts mineurs non visibles sans loupe.
    :cvar LIGHT_PLAYED: Manipulations légères, marques peu visibles.
    :cvar PLAYED: Usure visible compatible avec une utilisation régulière.
    :cvar POOR: Forte dégradation ou défauts majeurs.
    :cvar UNKNOWN: État non renseigné ou indéterminé.
    """

    MINT = "mint"
    NEAR_MINT = "near_mint"
    LIGHT_PLAYED = "light_played"
    PLAYED = "played"
    POOR = "poor"
    UNKNOWN = "unknown"
