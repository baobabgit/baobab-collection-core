"""Erreur lorsqu'une entrée de journal de mutation est introuvable."""

from .baobab_collection_core_exception import BaobabCollectionCoreException


class MutationNotFoundException(BaobabCollectionCoreException):
    """Levée si l'identifiant ne correspond à aucune mutation connue du journal."""
