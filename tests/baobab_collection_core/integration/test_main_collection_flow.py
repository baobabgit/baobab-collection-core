"""Scénarios d'intégration : persistance mémoire + services métier + synchro abstraite."""

from __future__ import annotations

import pytest

from baobab_collection_core.application.sync_conflict_detector import SyncConflictDetector
from baobab_collection_core.application.sync_conflict_resolution_strategy import (
    ExplicitManualSyncConflictStrategy,
)
from baobab_collection_core.application.sync_core_service import SyncCoreService
from baobab_collection_core.domain.local_entity_kind import LocalEntityKind
from baobab_collection_core.domain.local_mutation_kind import LocalMutationKind
from baobab_collection_core.domain.physical_copy_business_status import PhysicalCopyBusinessStatus
from baobab_collection_core.domain.physical_copy_condition import PhysicalCopyCondition
from baobab_collection_core.domain.sync_conflict_kind import SyncConflictKind
from baobab_collection_core.domain.sync_delta_kind import SyncDeltaKind
from baobab_collection_core.domain.sync_dtos import (
    LocalEntitySyncSnapshot,
    RemoteEntitySyncSnapshot,
)
from baobab_collection_core.domain.sync_plan_action import SyncPlanAction
from baobab_collection_core.domain.sync_session_outcome import SyncSessionOutcome
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.domain.container_kind import ContainerKind
from tests.baobab_collection_core.integration.conftest import IntegrationHarness

pytestmark = pytest.mark.integration


class TestMainCollectionFlow:
    """Flux métier principal sur une pile entièrement mémoire."""

    def test_create_entities_attach_copy_and_business_counts(
        self, integration_harness: IntegrationHarness
    ) -> None:
        """Usager, carte, copie, contenant, rattachement et agrégats d'inventaire."""
        h = integration_harness
        user = h.user_app.create_user("Alex Collectionneur", h.moment)
        card = h.card_app.create_card("Dragon doré", h.moment, external_id="SET-001", language="FR")
        box = h.container_app.create_container("Boîte A", ContainerKind.BOX, h.moment)
        copy = h.copy_app.create_copy(
            card.entity_id,
            user.entity_id,
            h.moment,
            physical_condition=PhysicalCopyCondition.NEAR_MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
        )
        assert copy.container_id is None
        h.copy_app.attach_container(copy.entity_id, h.moment, box.entity_id)
        reloaded = h.copy_app.get_copy_by_id(copy.entity_id)
        assert reloaded.container_id is not None
        assert reloaded.container_id.value == box.entity_id.value

        assert h.business.count_distinct_cards_in_collection() == 1
        assert h.business.count_total_copies_in_inventory() == 1
        assert h.business.count_available_copies() == 1
        view = h.business.list_container_contents(box.entity_id)
        assert len(view.physical_copies) == 1
        assert view.physical_copies[0].entity_id.value == copy.entity_id.value

    def test_local_mutation_recorded_and_extracted(
        self, integration_harness: IntegrationHarness
    ) -> None:
        """Journal offline-first : écriture puis extraction des pending."""
        h = integration_harness
        user = h.user_app.create_user("Sam Journal", h.moment)
        entry = h.mutations.record_from_entity_snapshot(
            entity_kind=LocalEntityKind.COLLECTION_USER,
            entity_id=user.entity_id,
            kind=LocalMutationKind.CREATE,
            metadata=user.metadata,
            recorded_at=h.moment,
        )
        pending = h.mutations.extract_pending_changes()
        assert len(pending) == 1
        assert pending[0].mutation_id.value == entry.mutation_id.value
        h.mutations.acknowledge_mutations((entry.mutation_id,))
        assert h.mutations.extract_pending_changes() == ()

    def test_simulated_sync_builds_plan_and_marks_synced_on_metadata(
        self, integration_harness: IntegrationHarness
    ) -> None:
        """Écart PUSH tant que le client est DIRTY, puis alignement après accusé synchro."""
        h = integration_harness
        card = h.card_app.create_card("Carte synchro", h.moment)
        sync = SyncCoreService()
        local_dirty = LocalEntitySyncSnapshot(
            entity_id=card.entity_id,
            entity_kind=LocalEntityKind.COLLECTION_CARD,
            version=card.metadata.version.value,
            sync_state=card.metadata.sync_state,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=card.entity_id,
            present=True,
            version=card.metadata.version.value,
            is_logically_deleted=False,
        )
        delta = sync.compare(local_dirty, remote)
        plan = sync.build_plan((delta,), plan_id="integ-plan")
        assert len(plan.items) == 1
        assert plan.items[0].action is SyncPlanAction.PUSH

        meta = sync.apply_entity_outcome_to_metadata(
            card.metadata,
            SyncSessionOutcome.SYNCED,
            h.moment,
            confirmed_remote_version=card.metadata.version.value,
        )
        assert meta.sync_state is SyncState.SYNCED
        local_clean = LocalEntitySyncSnapshot(
            entity_id=card.entity_id,
            entity_kind=LocalEntityKind.COLLECTION_CARD,
            version=meta.version.value,
            sync_state=meta.sync_state,
            is_logically_deleted=False,
        )
        delta_after = sync.compare(local_clean, remote)
        plan_after = sync.build_plan((delta_after,))
        assert plan_after.items[0].action is SyncPlanAction.NO_OP

    def test_simulated_conflict_version_divergence(
        self, integration_harness: IntegrationHarness
    ) -> None:
        """Distant plus récent + client dirty : cœur sync et détecteur alignés sur un conflit."""
        h = integration_harness
        user = h.user_app.create_user("Pat Conflit", h.moment)
        local = LocalEntitySyncSnapshot(
            entity_id=user.entity_id,
            entity_kind=LocalEntityKind.COLLECTION_USER,
            version=1,
            sync_state=SyncState.DIRTY,
            is_logically_deleted=False,
        )
        remote = RemoteEntitySyncSnapshot(
            entity_id=user.entity_id,
            present=True,
            version=4,
            is_logically_deleted=False,
        )
        delta = SyncCoreService().compare(local, remote)
        assert delta.kind is SyncDeltaKind.CONFLICT

        conflict = SyncConflictDetector().detect(local, remote)
        assert conflict is not None
        assert conflict.kind is SyncConflictKind.VERSION_DIVERGENCE

        decision = ExplicitManualSyncConflictStrategy().resolve(
            conflict,
            local=local,
            remote=remote,
        )
        assert decision.outcome is SyncSessionOutcome.CONFLICT
        assert decision.requires_manual_resolution is True
