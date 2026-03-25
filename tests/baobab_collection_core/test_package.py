"""Tests d'import et d'export du package racine."""

import importlib
import importlib.metadata
from unittest.mock import patch

import baobab_collection_core as bcc


class TestPackageImports:
    """Vérifie que le package s'installe et s'importe correctement."""

    def test_import_package(self) -> None:
        """Le symbole du package doit être résolu après installation."""
        assert bcc.__name__ == "baobab_collection_core"

    def test_version_is_non_empty_string(self) -> None:
        """La version publiée doit être une chaîne non vide."""
        assert isinstance(bcc.__version__, str)
        assert len(bcc.__version__) > 0

    def test_root_exception_reexported(self) -> None:
        """L'exception racine doit être accessible depuis le package racine."""
        assert bcc.BaobabCollectionCoreException is not None
        assert issubclass(bcc.BaobabCollectionCoreException, Exception)

    def test_version_fallback_when_metadata_missing(self) -> None:
        """Sans métadonnées installées, ``__version__`` doit valoir la repli."""
        with patch(
            "importlib.metadata.version",
            side_effect=importlib.metadata.PackageNotFoundError,
        ):
            importlib.reload(bcc)
            assert bcc.__version__ == "0.12.0"
        importlib.reload(bcc)
