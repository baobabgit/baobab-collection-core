"""Tests unitaires pour :class:`PhysicalCopy`."""

from datetime import datetime, timedelta, timezone

import pytest

from baobab_collection_core.domain.audit_timestamps import AuditTimestamps
from baobab_collection_core.domain.collection_card import UNSET
from baobab_collection_core.domain.domain_id import DomainId
from baobab_collection_core.domain.entity_metadata import EntityMetadata
from baobab_collection_core.domain.entity_version import EntityVersion
from baobab_collection_core.domain.physical_copy import PhysicalCopy
from baobab_collection_core.domain.physical_copy_business_status import PhysicalCopyBusinessStatus
from baobab_collection_core.domain.physical_copy_condition import PhysicalCopyCondition
from baobab_collection_core.domain.sync_state import SyncState
from baobab_collection_core.exceptions.invalid_physical_copy_exception import (
    InvalidPhysicalCopyException,
)


class TestPhysicalCopy:
    """Règles métier des exemplaires physiques."""

    @staticmethod
    def _now() -> datetime:
        return datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc)

    def _base_copy(
        self,
        *,
        container_id: DomainId | None = None,
    ) -> PhysicalCopy:
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        return PhysicalCopy.create(
            DomainId("22222222-2222-4222-8222-222222222222"),
            DomainId("00000000-0000-4000-8000-00000000c4d0"),
            DomainId("11111111-1111-4111-8111-111111111111"),
            metadata,
            physical_condition=PhysicalCopyCondition.NEAR_MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
            container_id=container_id,
            location_note="  Rack A  ",
            language="fr",
            finish="holo",
            notes="Chercher sleeve",
        )

    def test_create_nominal(self) -> None:
        """Création avec normalisation des champs texte optionnels."""
        copy = self._base_copy()
        assert copy.card_id.value == "00000000-0000-4000-8000-00000000c4d0"
        assert copy.owner_user_id.value == "11111111-1111-4111-8111-111111111111"
        assert copy.location_note == "Rack A"
        assert copy.language == "fr"
        assert copy.finish == "holo"
        assert copy.notes == "Chercher sleeve"
        assert copy.container_id is None

    def test_optional_text_too_long_raises(self) -> None:
        """Limite de taille appliquée aux champs texte."""
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        with pytest.raises(InvalidPhysicalCopyException):
            PhysicalCopy.create(
                DomainId("22222222-2222-4222-8222-222222222222"),
                DomainId("00000000-0000-4000-8000-00000000c4d0"),
                DomainId("11111111-1111-4111-8111-111111111111"),
                metadata,
                physical_condition=PhysicalCopyCondition.MINT,
                business_status=PhysicalCopyBusinessStatus.ACTIVE,
                notes="x" * 4001,
            )

    def test_blank_optional_normalized_to_none(self) -> None:
        """Chaînes vides après trim -> None."""
        moment = self._now()
        stamps = AuditTimestamps(created_at=moment, updated_at=moment)
        metadata = EntityMetadata(
            timestamps=stamps,
            version=EntityVersion(0),
            sync_state=SyncState.CLEAN,
        )
        copy = PhysicalCopy.create(
            DomainId("22222222-2222-4222-8222-222222222222"),
            DomainId("00000000-0000-4000-8000-00000000c4d0"),
            DomainId("11111111-1111-4111-8111-111111111111"),
            metadata,
            physical_condition=PhysicalCopyCondition.MINT,
            business_status=PhysicalCopyBusinessStatus.ACTIVE,
            location_note="   ",
        )
        assert copy.location_note is None

    def test_update_details_bumps_dirty(self) -> None:
        """Mutation descriptive synchronisée avec métadonnées."""
        copy = self._base_copy()
        later = copy.metadata.timestamps.updated_at + timedelta(minutes=10)
        copy.update_details(later, notes="Rien à signaler")
        assert copy.notes == "Rien à signaler"
        assert copy.metadata.version.value == 1
        assert copy.metadata.sync_state is SyncState.DIRTY

    def test_update_details_unset_preserves(self) -> None:
        """UNSET laisse les champs inchangés pour un patch partiel."""
        copy = self._base_copy()
        before = copy.language
        moment = copy.metadata.timestamps.updated_at + timedelta(minutes=1)
        copy.update_details(moment, finish="reverse", language=UNSET)
        assert copy.language == before
        assert copy.finish == "reverse"

    def test_change_physical_condition(self) -> None:
        """Transition d'état matériel."""
        copy = self._base_copy()
        moment = copy.metadata.timestamps.updated_at + timedelta(seconds=5)
        copy.change_physical_condition(moment, PhysicalCopyCondition.PLAYED)
        assert copy.physical_condition is PhysicalCopyCondition.PLAYED

    def test_change_business_status(self) -> None:
        """Transition de statut métier."""
        copy = self._base_copy()
        moment = copy.metadata.timestamps.updated_at + timedelta(seconds=5)
        copy.change_business_status(moment, PhysicalCopyBusinessStatus.ON_LOAN)
        assert copy.business_status is PhysicalCopyBusinessStatus.ON_LOAN

    def test_attach_and_detach_container(self) -> None:
        """Rattachement puis détachement d'un contenant."""
        copy = self._base_copy()
        cid = DomainId("33333333-3333-4333-8333-333333333333")
        m1 = copy.metadata.timestamps.updated_at + timedelta(seconds=1)
        copy.attach_to_container(m1, cid)
        assert copy.container_id == cid
        m2 = m1 + timedelta(seconds=1)
        copy.detach_from_container(m2)
        assert copy.container_id is None

    def test_attach_same_container_no_extra_bump(self) -> None:
        """Ré-attacher le même contenant ne crée pas de mutation inutile."""
        cid = DomainId("33333333-3333-4333-8333-333333333333")
        copy = self._base_copy(container_id=cid)
        version_before = copy.metadata.version.value
        copy.attach_to_container(
            copy.metadata.timestamps.updated_at + timedelta(seconds=2),
            cid,
        )
        assert copy.metadata.version.value == version_before

    def test_detach_without_container_no_op(self) -> None:
        """Détacher sans contenant ne modifie pas la version."""
        copy = self._base_copy()
        version_before = copy.metadata.version.value
        copy.detach_from_container(copy.metadata.timestamps.updated_at + timedelta(seconds=3))
        assert copy.metadata.version.value == version_before

    def test_soft_delete_marks_metadata(self) -> None:
        """Suppression logique : synchro DELETED et cycle de vie archivé."""
        copy = self._base_copy()
        moment = copy.metadata.timestamps.updated_at + timedelta(hours=1)
        copy.soft_delete(moment)
        assert copy.is_logically_deleted is True
        assert copy.metadata.sync_state is SyncState.DELETED

    def test_soft_delete_twice_raises(self) -> None:
        """Idempotence explicite refusée côté domaine."""
        copy = self._base_copy()
        moment = copy.metadata.timestamps.updated_at + timedelta(hours=1)
        copy.soft_delete(moment)
        with pytest.raises(InvalidPhysicalCopyException):
            copy.soft_delete(moment + timedelta(seconds=1))

    def test_mutations_forbidden_after_soft_delete(self) -> None:
        """Copie supprimée : plus de mutation métier."""
        copy = self._base_copy()
        moment = copy.metadata.timestamps.updated_at + timedelta(hours=1)
        copy.soft_delete(moment)
        with pytest.raises(InvalidPhysicalCopyException):
            copy.change_physical_condition(
                moment + timedelta(seconds=5), PhysicalCopyCondition.POOR
            )
