"""Erreur lorsque l'usager demandé n'existe pas dans le référentiel."""

from .baobab_collection_core_exception import BaobabCollectionCoreException


class UserNotFoundException(BaobabCollectionCoreException):
    """Levée lorsqu'aucun usager ne correspond à l'identifiant demandé.

    :param args: Message et contexte pour diagnostiquer l'échec.
    """
