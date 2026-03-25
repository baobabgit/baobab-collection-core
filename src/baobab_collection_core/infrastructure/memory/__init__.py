"""Adaptateurs mémoire de référence pour les ports de persistance (tests, prototypage)."""

from baobab_collection_core.infrastructure.memory.in_memory_card_repository import (
    InMemoryCardRepository,
)
from baobab_collection_core.infrastructure.memory.in_memory_container_repository import (
    InMemoryContainerRepository,
)
from baobab_collection_core.infrastructure.memory.in_memory_local_mutation_journal import (
    InMemoryLocalMutationJournal,
)
from baobab_collection_core.infrastructure.memory.in_memory_physical_copy_repository import (
    InMemoryPhysicalCopyRepository,
)
from baobab_collection_core.infrastructure.memory.in_memory_user_repository import (
    InMemoryUserRepository,
)

__all__: list[str] = [
    "InMemoryCardRepository",
    "InMemoryContainerRepository",
    "InMemoryLocalMutationJournal",
    "InMemoryPhysicalCopyRepository",
    "InMemoryUserRepository",
]
