"""Le manifeste projet doit rester aligné avec la release stable documentée."""

from __future__ import annotations

import pathlib
import re

import tomllib


def test_pyproject_declares_stable_1_0_0() -> None:
    """Évite une régression du classifier ou de la version dans pyproject.toml."""
    root = pathlib.Path(__file__).resolve().parents[2]
    raw = (root / "pyproject.toml").read_bytes()
    data = tomllib.loads(raw.decode("utf-8"))
    project = data["project"]
    assert project["version"] == "1.0.0"
    classifiers: list[str] = project["classifiers"]
    assert "Development Status :: 5 - Production/Stable" in classifiers
    assert not any(re.search(r"pre-?alpha", c, re.I) for c in classifiers)
