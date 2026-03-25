"""Erreur lorsque les données d'un usager violent des règles métier."""

from .validation_exception import ValidationException


class InvalidUserException(ValidationException):
    """Levée pour un usager intraitable (champs invalides, transition interdite, etc.).

    :param args: Détails transmis à :class:`ValidationException`.
    """
