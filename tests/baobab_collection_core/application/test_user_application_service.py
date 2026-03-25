"""Tests applicatifs du :class:`UserApplicationService`."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.application.user_application_service import UserApplicationService
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.exceptions import (
    DuplicateUserException,
    InvalidUserException,
    UserNotFoundException,
)
from tests.baobab_collection_core.support.in_memory_user_repository import InMemoryUserRepository


class TestUserApplicationService:
    """Scénarios create / update / deactivate / lecture."""

    @staticmethod
    def _moment() -> datetime:
        return datetime(2026, 3, 25, 12, 0, tzinfo=timezone.utc)

    def _service(self) -> tuple[UserApplicationService, InMemoryUserRepository]:
        repo = InMemoryUserRepository()
        return UserApplicationService(repo), repo

    def test_create_user_nominal(self) -> None:
        """Création avec persistance et état DIRTY initial côté métadonnées."""
        svc, _ = self._service()
        user = svc.create_user("Bob", self._moment())
        assert user.is_active is True
        assert user.display_name == "Bob"
        assert user.metadata.sync_state.value == "dirty"
        assert user.metadata.version.value == 0

    def test_create_user_rejects_duplicate_name_case_insensitive(self) -> None:
        """Le port détecte un doublon insensible à la casse."""
        svc, _ = self._service()
        svc.create_user("Charlie", self._moment())
        with pytest.raises(DuplicateUserException):
            svc.create_user("charlie", self._moment())

    def test_create_user_invalid_name(self) -> None:
        """Les règles d'entité remontent via l'application."""
        svc, _ = self._service()
        with pytest.raises(InvalidUserException):
            svc.create_user("  ", self._moment())

    def test_update_user_changes_name_and_version(self) -> None:
        """Mise à jour persistée."""
        svc, _ = self._service()
        user = svc.create_user("Dana", self._moment())
        later = self._moment() + timedelta(minutes=10)
        updated = svc.update_user(user.entity_id, "Dana Lee", later)
        assert updated.display_name == "Dana Lee"
        assert updated.metadata.version.value == 1

    def test_update_user_duplicate_for_another_identity(self) -> None:
        """Impossible de voler le nom d'un autre usager."""
        svc, _ = self._service()
        svc.create_user("Eve", self._moment())
        second = svc.create_user("Frank", self._moment() + timedelta(seconds=1))
        with pytest.raises(DuplicateUserException):
            svc.update_user(second.entity_id, "eve", self._moment() + timedelta(minutes=5))

    def test_get_user_not_found(self) -> None:
        """Erreur explicite si l'identifiant n'existe pas."""
        svc, _ = self._service()
        missing = DomainId("00000000-0000-4000-8000-00000000dead")
        with pytest.raises(UserNotFoundException):
            svc.get_user_by_id(missing)

    def test_list_users_returns_saved_entities(self) -> None:
        """La liste matérialise le contenu du port."""
        svc, _ = self._service()
        first = svc.create_user("Georgia", self._moment())
        second = svc.create_user("Hector", self._moment() + timedelta(seconds=2))
        users = svc.list_users()
        assert len(users) == 2
        assert {u.entity_id.value for u in users} == {
            first.entity_id.value,
            second.entity_id.value,
        }

    def test_deactivate_user_flow(self) -> None:
        """Désactivation persistée et idempotence contrôlée côté domaine."""
        svc, _ = self._service()
        user = svc.create_user("Ivy", self._moment())
        later = self._moment() + timedelta(hours=2)
        deactivated = svc.deactivate_user(user.entity_id, later)
        assert deactivated.is_active is False
        assert deactivated.metadata.version.value == 1
        with pytest.raises(InvalidUserException):
            svc.deactivate_user(user.entity_id, later + timedelta(minutes=5))
