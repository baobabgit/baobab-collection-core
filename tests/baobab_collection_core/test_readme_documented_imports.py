"""Fumée : imports alignés sur les exemples du README (non exécution complète des flux)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from baobab_collection_core.application.collection_business_service import CollectionBusinessService
from baobab_collection_core.application.sync_core_service import SyncCoreService
from baobab_collection_core.application.user_application_service import UserApplicationService
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.sync_delta_kind import SyncDeltaKind
from baobab_collection_core.domain.sync_dtos import (
    LocalEntitySyncSnapshot,
    RemoteEntitySyncSnapshot,
)
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.infrastructure.memory import (
    InMemoryCardRepository,
    InMemoryContainerRepository,
    InMemoryPhysicalCopyRepository,
    InMemoryUserRepository,
)


def test_readme_imports_resolve() -> None:
    """Les chemins d'import documentés pour les consommateurs doivent rester valides."""
    moment = datetime.now(timezone.utc)
    label = f"readme_smoke_{uuid.uuid4().hex[:8]}"
    user = UserApplicationService(InMemoryUserRepository()).create_user(label, moment)
    assert user.display_name == label

    business = CollectionBusinessService(
        InMemoryCardRepository(),
        InMemoryPhysicalCopyRepository(),
        InMemoryContainerRepository(),
    )
    assert business.count_distinct_cards_in_collection() == 0

    eid = DomainId("550e8400-e29b-41d4-a716-446655440000")
    local = LocalEntitySyncSnapshot(
        entity_id=eid,
        entity_kind=LocalEntityKind.COLLECTION_USER,
        version=1,
        sync_state=SyncState.DIRTY,
        is_logically_deleted=False,
    )
    remote = RemoteEntitySyncSnapshot(
        entity_id=eid,
        present=True,
        version=3,
        is_logically_deleted=False,
    )
    delta = SyncCoreService().compare(local, remote)
    assert delta.kind is SyncDeltaKind.CONFLICT
