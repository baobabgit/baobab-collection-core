"""Erreur lorsque des instantanés de synchro sont incohérents."""

from .validation_exception import ValidationException


class InvalidSyncSnapshotException(ValidationException):
    """Instantané local/distant impossible à comparer ou version non monotone."""
