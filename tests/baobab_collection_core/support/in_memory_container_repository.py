"""Rétrocompatibilité des tests : délègue à l'infrastructure officielle."""

from baobab_collection_core.infrastructure.memory import InMemoryContainerRepository

__all__: list[str] = ["InMemoryContainerRepository"]
