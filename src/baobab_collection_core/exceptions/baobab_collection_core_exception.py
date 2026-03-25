"""Définition de l'exception racine du projet."""


class BaobabCollectionCoreException(Exception):
    """Exception de base pour toutes les erreurs spécifiques au projet.

    Les exceptions personnalisées de *baobab-collection-core* doivent hériter
    de cette classe afin de permettre un traitement d'erreurs homogène.

    :param args: Valeurs transmises au constructeur de :class:`Exception`.

    :Example:

        Lever une erreur projet::

            raise BaobabCollectionCoreException("message d'erreur")
    """
