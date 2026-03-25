"""Erreur lorsque les données d'une carte de collection sont invalides."""

from .validation_exception import ValidationException


class InvalidCardException(ValidationException):
    """Levée lorsqu'une règle sur la référence carte est violée.

    :param args: Détails transmis à :class:`ValidationException`.
    """
