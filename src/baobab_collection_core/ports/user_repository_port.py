"""Contrat de persistance pour l'entité :class:`CollectionUser`."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from baobab_collection_core.domain.collection_user import CollectionUser
from baobab_collection_core.domain.domain_id import DomainId


class UserRepositoryPort(ABC):
    """Port hexagonal : lecture/écriture des usagers sans technologie imposée.

    Les implémentations concrètes vivent hors de ce package ou dans des modules
    d'infrastructure dédiés (SQL, fichiers, mémoire de test, etc.).
    """

    @abstractmethod
    def get_by_id(self, user_id: DomainId) -> CollectionUser | None:
        """Retourne l'usager correspondant ou ``None`` s'il est absent."""

    @abstractmethod
    def list_users(self) -> Sequence[CollectionUser]:
        """Liste tous les usagers connus (ordre laissé à l'implémentation)."""

    @abstractmethod
    def save(self, user: CollectionUser) -> None:
        """Crée ou met à jour l'usager fourni (upsert logique)."""

    @abstractmethod
    def exists_duplicate_display_name(
        self,
        display_name: str,
        *,
        exclude_user_id: DomainId | None = None,
    ) -> bool:
        """Détecte un conflit sur le nom affiché (comparaison ``casefold``).

        :param display_name: Candidat à vérifier.
        :param exclude_user_id: Permet d'ignorer l'usager en cours de mise à jour.
        :returns: ``True`` si un autre usager porte déjà le même nom normalisé.
        """
