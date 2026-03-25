"""Rétrocompatibilité des tests : délègue à l'infrastructure officielle."""

from baobab_collection_core.infrastructure.memory import InMemoryUserRepository

__all__: list[str] = ["InMemoryUserRepository"]
