"""Erreurs de validation liées aux primitives de domaine."""

from .baobab_collection_core_exception import BaobabCollectionCoreException


class ValidationException(BaobabCollectionCoreException):
    """Levée lorsqu'une valeur ou un invariant de domaine est invalide.

    Préférer cette exception aux types built-in (:class:`ValueError`, etc.)
    pour toute règle portée par *baobab-collection-core*.

    :param args: Message et métadonnées transmises à :class:`BaobabCollectionCoreException`.
    """
