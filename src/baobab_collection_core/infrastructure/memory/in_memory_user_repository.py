"""Adaptateur mémoire pour le port des usagers."""

from __future__ import annotations

from collections.abc import Sequence

from baobab_collection_core.domain.collection_user import CollectionUser
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.ports.user_repository_port import UserRepositoryPort


class InMemoryUserRepository(UserRepositoryPort):
    """Stockage volatil indexé par identifiant d'usager."""

    __slots__ = ("_storage",)

    def __init__(self) -> None:
        self._storage: dict[str, CollectionUser] = {}

    def get_by_id(self, user_id: DomainId) -> CollectionUser | None:
        """Voir :meth:`UserRepositoryPort.get_by_id`."""
        return self._storage.get(user_id.value)

    def list_users(self) -> Sequence[CollectionUser]:
        """Tri déterministe par UUID pour des listes stables entre appels."""
        return tuple(sorted(self._storage.values(), key=lambda user: user.entity_id.value))

    def save(self, user: CollectionUser) -> None:
        """Upsert de l'usager fourni."""
        self._storage[user.entity_id.value] = user

    def exists_duplicate_display_name(
        self,
        display_name: str,
        *,
        exclude_user_id: DomainId | None = None,
    ) -> bool:
        """Aligné sur :meth:`CollectionUser.display_name_key`."""
        key = CollectionUser.display_name_key(display_name)
        exclude = exclude_user_id.value if exclude_user_id is not None else None
        for uid, existing in self._storage.items():
            if exclude is not None and uid == exclude:
                continue
            if CollectionUser.display_name_key(existing.display_name) == key:
                return True
        return False
