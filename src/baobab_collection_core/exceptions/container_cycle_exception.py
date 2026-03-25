"""Erreur lorsque la hiérarchie des contenants formerait un cycle."""

from .baobab_collection_core_exception import BaobabCollectionCoreException


class ContainerCycleException(BaobabCollectionCoreException):
    """Levée si un parent impliquerait un contenant comme ancêtre de lui-même."""
