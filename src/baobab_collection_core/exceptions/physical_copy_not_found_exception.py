"""Erreur lorsque la copie physique demandée est introuvable ou inactive."""

from .baobab_collection_core_exception import BaobabCollectionCoreException


class PhysicalCopyNotFoundException(BaobabCollectionCoreException):
    """Levée si aucun exemplaire actif ne correspond à l'identifiant fourni.

    :param args: Message et contexte pour diagnostiquer l'échec.
    """
