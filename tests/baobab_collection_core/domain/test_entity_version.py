"""Tests pour :class:`EntityVersion`."""

from typing import Any, cast

import pytest

from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.exceptions import ValidationException


class TestEntityVersion:
    """Comportement du compteur optimiste."""

    def test_zero_allowed(self) -> None:
        """Création initiale possible à 0."""
        assert EntityVersion(0).value == 0

    def test_negative_rejected(self) -> None:
        """Les versions négatives sont invalides."""
        with pytest.raises(ValidationException):
            EntityVersion(-1)

    def test_bool_rejected(self) -> None:
        """Évite l'ambiguïté bool / int."""
        with pytest.raises(ValidationException):
            EntityVersion(cast(Any, True))

    def test_next_increments(self) -> None:
        """next() produit un nouveau value object monotone."""
        v0 = EntityVersion(0)
        v1 = v0.next()
        assert v1.value == 1
        assert v0.value == 0

    def test_from_primitive(self) -> None:
        """Reconstruction depuis un entier JSON."""
        assert EntityVersion.from_primitive(3).value == 3

    def test_from_primitive_rejects_bool(self) -> None:
        """bool explicite refusé."""
        with pytest.raises(ValidationException):
            EntityVersion.from_primitive(True)
