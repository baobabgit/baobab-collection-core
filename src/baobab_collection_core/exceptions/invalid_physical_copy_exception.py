"""Erreur lorsque les données d'une copie physique sont invalides ou incohérentes."""

from .validation_exception import ValidationException


class InvalidPhysicalCopyException(ValidationException):
    """Levée pour une copie inexploitable ou une transition interdite.

    :param args: Détails transmis à :class:`ValidationException`.
    """
