"""Erreur lorsque les paramètres d'une mutation locale sont invalides."""

from .validation_exception import ValidationException


class InvalidLocalMutationException(ValidationException):
    """Levée pour incohérences sur le journal (versions négatives, payload illégal, etc.)."""
