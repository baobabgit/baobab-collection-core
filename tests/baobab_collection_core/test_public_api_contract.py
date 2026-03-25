"""Contrat d'exposition publique : package racine et sous-packages `__all__`."""

from __future__ import annotations

import baobab_collection_core as bcc
from baobab_collection_core import application, domain, exceptions, infrastructure, ports


def test_root_all_matches_documented_minimal_surface() -> None:
    """Le README annonce une racine réduite : seulement l'exception de base et la version."""
    assert set(bcc.__all__) == {"BaobabCollectionCoreException", "__version__"}


def test_subpackages_export_only_via_all() -> None:
    """Chaque sous-package listé expose un ``__all__`` non vide (discipline public API)."""
    for pkg, name in (
        (application, "application"),
        (domain, "domain"),
        (exceptions, "exceptions"),
        (infrastructure, "infrastructure"),
        (ports, "ports"),
    ):
        assert hasattr(pkg, "__all__"), f"missing __all__ on {name}"
        assert len(pkg.__all__) > 0, f"empty __all__ on {name}"
