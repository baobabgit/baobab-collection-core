"""Tests pour :class:`ValidationException`."""

import pytest

from baobab_collection_core.exceptions import BaobabCollectionCoreException, ValidationException


class TestValidationException:
    """Vérifie la hiérarchie d'erreurs projet."""

    def test_subclass_of_core_exception(self) -> None:
        """La validation doit rester sous l'exception racine."""
        assert issubclass(ValidationException, BaobabCollectionCoreException)

    def test_can_raise_with_message(self) -> None:
        """Message utilisateur conservé."""
        with pytest.raises(ValidationException) as info:
            raise ValidationException("champ invalide")
        assert str(info.value) == "champ invalide"
