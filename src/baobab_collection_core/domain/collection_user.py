"""Entité métier représentant un usager de la collection."""

from __future__ import annotations

from datetime import datetime

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_base import EntityBase
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.invalid_user_exception import InvalidUserException

_MAX_DISPLAY_NAME_LEN = 256


class CollectionUser(EntityBase):
    """Usager identifiable avec nom affiché, statut d'activité et métadonnées versionnées.

    La désactivation est logique : l'entité reste stockée (pas de destruction physique par défaut).
    Toute mutation métier incrémente la version et marque l'état de synchro ``DIRTY``.

    :param entity_id: Identifiant immuable.
    :param display_name: Nom présenté dans l'interface (non vide après normalisation).
    :param is_active: ``False`` si l'usager ne doit plus être proposé par défaut.
    :param metadata: Bundle d'audit / version / synchro.

    :ivar _display_name: Stockage interne du libellé.
    :ivar _is_active: Indicateur d'activité métier.
    """

    __slots__ = ("_display_name", "_is_active")

    def __init__(
        self,
        entity_id: DomainId,
        display_name: str,
        is_active: bool,
        metadata: EntityMetadata,
    ) -> None:
        CollectionUser._validate_display_name(display_name)
        super().__init__(entity_id, metadata)
        self._display_name = display_name.strip()
        self._is_active = is_active

    @property
    def display_name(self) -> str:
        """Libellé affiché pour l'usager."""
        return self._display_name

    @property
    def is_active(self) -> bool:
        """Indique si l'usager est actif du point de vue métier."""
        return self._is_active

    @classmethod
    def create(
        cls,
        entity_id: DomainId,
        display_name: str,
        metadata: EntityMetadata,
        *,
        is_active: bool = True,
    ) -> CollectionUser:
        """Fabrique contrôlée alignée sur une :class:`EntityMetadata` déjà initialisée.

        :param entity_id: Identifiant alloué par la couche applicative ou l'infra.
        :param display_name: Nom visible.
        :param metadata: Métadonnées cohérentes avec l'instant de création.
        :param is_active: Statut initial d'activité (défaut actif).
        :returns: Entité prête à être persistée.
        """
        return cls(entity_id, display_name, is_active, metadata)

    @staticmethod
    def display_name_key(display_name: str) -> str:
        """Clé de dédoublonnage sur le nom (strip + ``casefold`` unicode-safe)."""
        return display_name.strip().casefold()

    @staticmethod
    def validate_display_name(display_name: str) -> None:
        """Valide un libellé hors contexte d'entité (services applicatifs).

        :raises InvalidUserException: si le texte est vide ou trop long.
        """
        CollectionUser._validate_display_name(display_name)

    @staticmethod
    def _validate_display_name(display_name: str) -> None:
        stripped = display_name.strip()
        if not stripped:
            raise InvalidUserException("Le nom affiché de l'usager ne peut pas être vide.")
        if len(stripped) > _MAX_DISPLAY_NAME_LEN:
            raise InvalidUserException(
                f"Le nom affiché ne peut pas dépasser {_MAX_DISPLAY_NAME_LEN} caractères."
            )

    def update_display_name(self, display_name: str, moment: datetime) -> None:
        """Renomme l'usager en incrémentant la version et en marquant la synchro comme ``DIRTY``.

        :param display_name: Nouveau nom (mêmes règles que à la création).
        :param moment: Horodatage métier de la modification (timezone-aware).
        :raises InvalidUserException: si le nom est invalide.
        """
        CollectionUser._validate_display_name(display_name)
        new_meta = self._metadata.bump_version(moment).with_sync_state(SyncState.DIRTY)
        self.replace_metadata(new_meta)
        self._display_name = display_name.strip()

    def deactivate(self, moment: datetime) -> None:
        """Désactive l'usager sans le détruire.

        :param moment: Instant de la désactivation.
        :raises InvalidUserException: si l'usager est déjà inactif.
        """
        if not self._is_active:
            raise InvalidUserException("L'usager est déjà désactivé.")
        new_meta = self._metadata.bump_version(moment).with_sync_state(SyncState.DIRTY)
        self.replace_metadata(new_meta)
        self._is_active = False
