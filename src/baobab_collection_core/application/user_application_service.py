"""Cas d'usage applicatifs autour des usagers de collection."""

from __future__ import annotations

import uuid
from datetime import datetime

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.collection_user import CollectionUser
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.duplicate_user_exception import DuplicateUserException
from baobab_collection_core.exceptions.user_not_found_exception import UserNotFoundException
from baobab_collection_core.ports.user_repository_port import UserRepositoryPort


class UserApplicationService:
    """Orchestre la création, la maintenance et la consultation des usagers.

    Ne connaît aucun détail de stockage : toute persistance passe par :class:`UserRepositoryPort`.

    :param users: Repository injecté respectant le port projet.
    """

    __slots__ = ("_users",)

    def __init__(self, users: UserRepositoryPort) -> None:
        self._users = users

    def create_user(self, display_name: str, moment: datetime) -> CollectionUser:
        """Crée un nouvel usager actif avec métadonnées initiales cohérentes.

        :param display_name: Nom affiché (validé côté entité).
        :param moment: Horodatage d'audit pour ``created_at`` / ``updated_at``.
        :raises DuplicateUserException: si le nom est déjà utilisé (insensible à la casse).
        :returns: Entité persistée via le repository.
        """
        CollectionUser.validate_display_name(display_name)
        if self._users.exists_duplicate_display_name(display_name):
            raise DuplicateUserException(
                "Un usager avec ce nom affiché existe déjà dans la collection."
            )
        entity_id = DomainId(str(uuid.uuid4()))
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.DIRTY,
        )
        user = CollectionUser.create(entity_id, display_name, metadata)
        self._users.save(user)
        return user

    def update_user(self, user_id: DomainId, display_name: str, moment: datetime) -> CollectionUser:
        """Met à jour le nom affiché d'un usager existant.

        :raises UserNotFoundException: si l'identifiant est inconnu.
        :raises DuplicateUserException: si le nouveau nom entre en conflit.
        """
        CollectionUser.validate_display_name(display_name)
        user = self._require_user(user_id)
        if self._users.exists_duplicate_display_name(display_name, exclude_user_id=user_id):
            raise DuplicateUserException(
                "Un autre usager porte déjà ce nom affiché dans la collection."
            )
        user.update_display_name(display_name, moment)
        self._users.save(user)
        return user

    def deactivate_user(self, user_id: DomainId, moment: datetime) -> CollectionUser:
        """Désactive un usager existant.

        :raises UserNotFoundException: si l'identifiant est inconnu.
        """
        user = self._require_user(user_id)
        user.deactivate(moment)
        self._users.save(user)
        return user

    def get_user_by_id(self, user_id: DomainId) -> CollectionUser:
        """Récupère un usager ou lève une erreur explicite."""
        return self._require_user(user_id)

    def list_users(self) -> list[CollectionUser]:
        """Expose la vue liste du repository sous forme de liste matérialisée."""
        return list(self._users.list_users())

    def _require_user(self, user_id: DomainId) -> CollectionUser:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException(
                "Aucun usager ne correspond à l'identifiant fourni dans la collection."
            )
        return user
