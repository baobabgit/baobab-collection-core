"""Erreur de conflit lorsqu'un identifiant externe est déjà attribué à une autre carte."""

from .validation_exception import ValidationException


class DuplicateCardException(ValidationException):
    """Levée lorsque l'identifiant externe est déjà utilisé par une autre référence carte.

    :param args: Explication du doublon.
    """
