"""Fixtures partagées pour les tests d'intégration multi-couches."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from baobab_collection_core.application.card_application_service import CardApplicationService
from baobab_collection_core.application.collection_business_service import CollectionBusinessService
from baobab_collection_core.application.container_application_service import (
    ContainerApplicationService,
)
from baobab_collection_core.application.mutation_tracking_service import MutationTrackingService
from baobab_collection_core.application.physical_copy_application_service import (
    PhysicalCopyApplicationService,
)
from baobab_collection_core.application.user_application_service import UserApplicationService
from baobab_collection_core.infrastructure.memory import (
    InMemoryCardRepository,
    InMemoryContainerRepository,
    InMemoryLocalMutationJournal,
    InMemoryPhysicalCopyRepository,
    InMemoryUserRepository,
)


@dataclass
class IntegrationHarness:
    """Regroupe adaptateurs mémoire et services applicatifs pour un scénario bout-en-bout."""

    moment: datetime
    users: InMemoryUserRepository
    cards: InMemoryCardRepository
    copies: InMemoryPhysicalCopyRepository
    containers: InMemoryContainerRepository
    journal: InMemoryLocalMutationJournal
    user_app: UserApplicationService
    card_app: CardApplicationService
    copy_app: PhysicalCopyApplicationService
    container_app: ContainerApplicationService
    mutations: MutationTrackingService
    business: CollectionBusinessService


@pytest.fixture
def integration_harness() -> IntegrationHarness:
    """Construit un graphe de dépendances cohérent (une « collection » vierge)."""
    moment = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    users = InMemoryUserRepository()
    cards = InMemoryCardRepository()
    copies = InMemoryPhysicalCopyRepository()
    containers = InMemoryContainerRepository()
    journal = InMemoryLocalMutationJournal()
    user_app = UserApplicationService(users)
    card_app = CardApplicationService(cards)
    copy_app = PhysicalCopyApplicationService(copies)
    container_app = ContainerApplicationService(containers)
    mutations = MutationTrackingService(journal)
    business = CollectionBusinessService(cards, copies, containers)
    return IntegrationHarness(
        moment=moment,
        users=users,
        cards=cards,
        copies=copies,
        containers=containers,
        journal=journal,
        user_app=user_app,
        card_app=card_app,
        copy_app=copy_app,
        container_app=container_app,
        mutations=mutations,
        business=business,
    )
