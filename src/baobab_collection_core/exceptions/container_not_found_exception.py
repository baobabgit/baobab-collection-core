"""Erreur lorsque le contenant demandé est introuvable."""

from .baobab_collection_core_exception import BaobabCollectionCoreException


class ContainerNotFoundException(BaobabCollectionCoreException):
    """Levée si aucun contenant ne correspond à l'identifiant fourni."""
