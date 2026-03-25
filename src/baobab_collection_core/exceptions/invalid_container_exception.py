"""Erreur lorsque les données d'un contenant sont invalides."""

from .validation_exception import ValidationException


class InvalidContainerException(ValidationException):
    """Levée lorsqu'une règle métier sur un contenant est violée."""
