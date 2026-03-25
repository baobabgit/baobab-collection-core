"""Ports : interfaces (abstractions) vers l'extérieur (persistance, horloge, etc.)."""

from baobab_collection_core.ports.user_repository_port import UserRepositoryPort

__all__: list[str] = ["UserRepositoryPort"]
