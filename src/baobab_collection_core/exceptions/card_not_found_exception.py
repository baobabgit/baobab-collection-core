"""Erreur lorsque la carte demandée n'existe pas dans le référentiel."""

from .baobab_collection_core_exception import BaobabCollectionCoreException


class CardNotFoundException(BaobabCollectionCoreException):
    """Levée lorsqu'aucune carte ne correspond à l'identifiant fourni.

    :param args: Message et contexte pour diagnostiquer l'échec.
    """
