"""Classification des entités concernées par le journal de mutations locales."""

from enum import StrEnum


class LocalEntityKind(StrEnum):
    """Cible métier d'une :class:`~baobab_collection_core.domain.local_mutation.LocalMutation`.

    :cvar COLLECTION_CARD: Référence carte catalogue.
    :cvar PHYSICAL_COPY: Exemplaire physique.
    :cvar CONTAINER: Contenant de rangement.
    :cvar COLLECTION_USER: Usager de la collection.
    """

    COLLECTION_CARD = "collection_card"
    PHYSICAL_COPY = "physical_copy"
    CONTAINER = "container"
    COLLECTION_USER = "collection_user"
