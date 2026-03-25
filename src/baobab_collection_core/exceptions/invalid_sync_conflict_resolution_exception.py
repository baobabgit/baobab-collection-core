"""Stratégie ou contexte incompatible avec la résolution automatique demandée."""

from baobab_collection_core.exceptions.validation_exception import ValidationException


class InvalidSyncConflictResolutionException(ValidationException):
    """État distant manquant ou incohérent pour appliquer la stratégie choisie."""
