"""Identifiant opaque de domaine, matérialisé par un UUID."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from baobab_collection_core.exceptions.validation_exception import ValidationException


@dataclass(frozen=True, slots=True)
class DomainId:
    """Identifiant stable, typé et sérialisable pour entités et événements de domaine.

    La valeur est normalisée en minuscules conformément à :func:`uuid.UUID`.

    :ivar value: Représentation string d'un UUID valide.

    :Example::

        ident = DomainId(str(uuid.uuid4()))
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationException("L'identifiant de domaine ne peut pas être vide.")
        try:
            normalized = str(uuid.UUID(self.value.strip()))
        except ValueError as exc:
            raise ValidationException(
                "L'identifiant de domaine doit être un UUID RFC 4122 valide."
            ) from exc
        object.__setattr__(self, "value", normalized)

    def to_primitive(self) -> str:
        """Retourne la valeur brute prête pour sérialisation JSON ou persistance.

        :returns: La chaîne UUID normalisée.
        """
        return self.value

    @classmethod
    def from_primitive(cls, raw: object) -> DomainId:
        """Reconstruit un :class:`DomainId` depuis une valeur sérialisée.

        :param raw: Valeur attendue de type :class:`str` après validation.
        :returns: Identifiant validé.
        :raises ValidationException: si ``raw`` n'est pas une chaîne UUID valide.
        """
        if not isinstance(raw, str):
            raise ValidationException(
                "Un DomainId sérialisé doit être reconstruit depuis une chaîne (str)."
            )
        return cls(raw)
