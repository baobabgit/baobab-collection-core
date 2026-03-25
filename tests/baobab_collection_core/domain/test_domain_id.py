"""Tests pour :class:`DomainId`."""

import uuid

import pytest

from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.exceptions import ValidationException


class TestDomainId:
    """Validation et sérialisation d'identifiants."""

    def test_create_from_valid_uuid(self) -> None:
        """Accepte un UUID RFC 4122 et normalise la casse."""
        uid = uuid.uuid4()
        domain_id = DomainId(f"  {str(uid).upper()}  ")
        assert domain_id.value == str(uid)

    def test_empty_string_rejected(self) -> None:
        """Chaîne vide interdite."""
        with pytest.raises(ValidationException):
            DomainId("")

    def test_invalid_uuid_rejected(self) -> None:
        """Texte arbitraire rejeté."""
        with pytest.raises(ValidationException):
            DomainId("not-a-uuid")

    def test_to_and_from_primitive_round_trip(self) -> None:
        """Cycle sérialisation simple."""
        original = DomainId(str(uuid.uuid4()))
        restored = DomainId.from_primitive(original.to_primitive())
        assert restored == original

    def test_from_primitive_rejects_non_string(self) -> None:
        """Type strict côté désérialisation."""
        with pytest.raises(ValidationException):
            DomainId.from_primitive(123)
