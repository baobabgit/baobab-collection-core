"""Tests unitaires pour :class:`BaobabCollectionCoreException`."""

import pytest

from baobab_collection_core.exceptions import BaobabCollectionCoreException


class TestBaobabCollectionCoreException:
    """Vérifie le comportement de l'exception racine du projet."""

    def test_subclass_of_exception(self) -> None:
        """L'exception projet doit dériver de :class:`Exception`."""
        assert issubclass(BaobabCollectionCoreException, Exception)

    def test_can_raise_and_catch(self) -> None:
        """Lever l'exception doit permettre une capture typée."""
        with pytest.raises(BaobabCollectionCoreException) as exc_info:
            raise BaobabCollectionCoreException("erreur test")
        assert str(exc_info.value) == "erreur test"
