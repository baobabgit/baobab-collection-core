"""Implémentation mémoire de :class:`UserRepositoryPort` pour les tests."""

from __future__ import annotations

from collections.abc import Sequence

from baobab_collection_core.domain.collection_user import CollectionUser
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.ports.user_repository_port import UserRepositoryPort


class InMemoryUserRepository(UserRepositoryPort):
    """Stockage volatil en mémoire pour les tests applicatifs."""

    __slots__ = ("_storage",)

    def __init__(self) -> None:
        self._storage: dict[str, CollectionUser] = {}

    def get_by_id(self, user_id: DomainId) -> CollectionUser | None:
        """Voir :meth:`UserRepositoryPort.get_by_id`."""
        return self._storage.get(user_id.value)

    def list_users(self) -> Sequence[CollectionUser]:
        """Retourne une liste triée par identifiant pour des assertions stables."""
        return tuple(sorted(self._storage.values(), key=lambda user: user.entity_id.value))

    def save(self, user: CollectionUser) -> None:
        """Enregistre ou remplace la copie courante."""
        self._storage[user.entity_id.value] = user

    def exists_duplicate_display_name(
        self,
        display_name: str,
        *,
        exclude_user_id: DomainId | None = None,
    ) -> bool:
        """Réutilise la même normalisation que le domaine."""
        key = CollectionUser.display_name_key(display_name)
        exclude = exclude_user_id.value if exclude_user_id is not None else None
        for uid, existing in self._storage.items():
            if exclude is not None and uid == exclude:
                continue
            if CollectionUser.display_name_key(existing.display_name) == key:
                return True
        return False
