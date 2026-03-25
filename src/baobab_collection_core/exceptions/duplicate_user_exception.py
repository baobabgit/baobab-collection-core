"""Erreur de conflit lorsqu'un second usager porterait un nom déjà réservé."""

from .validation_exception import ValidationException


class DuplicateUserException(ValidationException):
    """Levée lorsque la création ou la mise à jour créerait un doublon de nom affiché.

    :param args: Message décrivant le conflit (nom en cause, stratégie possible).
    """
