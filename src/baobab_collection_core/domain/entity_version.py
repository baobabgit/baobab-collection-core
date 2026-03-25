"""Numéro de version d'entité pour contrôle d'optimistic concurrency."""

from __future__ import annotations

from dataclasses import dataclass

from baobab_collection_core.exceptions.validation_exception import ValidationException


@dataclass(frozen=True, slots=True)
class EntityVersion:
    """Entier non négatif représentant la révision logique d'une ressource.

    :ivar value: Compteur de version (0 autorisé pour une création initiale).

    :Example::

        v0 = EntityVersion(0)
        v1 = v0.next()
    """

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool):
            raise ValidationException("EntityVersion n'accepte pas les valeurs booléennes.")
        if self.value < 0:
            raise ValidationException("La version d'entité doit être un entier >= 0.")

    def next(self) -> EntityVersion:
        """Calcule la révision suivante sans muter l'instance (value object).

        :returns: Nouvelle version incrémentée de un.
        """
        return EntityVersion(self.value + 1)

    def to_primitive(self) -> int:
        """Représentation JSON-friendly."""
        return self.value

    @classmethod
    def from_primitive(cls, raw: object) -> EntityVersion:
        """Reconstruction depuis une valeur sérialisée (entier)."""
        if not isinstance(raw, int) or isinstance(raw, bool):
            raise ValidationException("EntityVersion attend un entier lors de la désérialisation.")
        return cls(raw)
