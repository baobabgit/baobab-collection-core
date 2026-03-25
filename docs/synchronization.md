# Synchronisation — modèle logique

La synchronisation est conçue pour fonctionner **sans couplage réseau** dans le cœur : transport, sérialisation et authentification relèvent d’adaptateurs externes.

## États (`SyncState`)

| Valeur | Rôle typique |
|--------|----------------|
| `clean` | Pas de modification locale en attente de propagation. |
| `dirty` | Changements locaux non poussés. |
| `synced` | Dernière synchro réussie avec le pair. |
| `conflict` | Divergence nécessitant arbitrage. |
| `sync_error` | Dernière tentative en erreur retentable. |
| `deleted` | Suppression logique à propager. |

Ces valeurs nourrissent à la fois les entités (`EntityMetadata`) et les instantanés de comparaison.

## Instantanés et écarts

- **`LocalEntitySyncSnapshot`** : identité, kind, version entière, `SyncState`, tombeau logique, et champs optionnels (`parent_container_id`, `content_fingerprint`, `external_business_key`) pour affiner la détection.
- **`RemoteEntitySyncSnapshot`** : présence (`present`), version si présent, tombeau, mêmes champs optionnels côté pair.

**`SyncCoreService.compare`** produit un **`EntitySyncDelta`** avec un **`SyncDeltaKind`** : `none`, `push`, `pull`, `conflict`.

**`build_plan`** agrège des deltas en **`SyncPlan`** d’**items** (`SyncPlanAction` : `no_op`, `push`, `pull`, `report_conflict`).

Les résultats applicatifs utilisent **`SyncSessionOutcome`** (`synced`, `pending`, `conflict`, `sync_error`) et peuvent être consolidés sur un lot (**`SynchronizationBatchResult`**).

**`apply_entity_outcome_to_metadata`** met à jour `EntityMetadata` selon l’issue (y compris version distante confirmée pour `SYNCED`).

## Port distant

**`RemoteEntitySyncSnapshotPort.fetch_snapshot(entity_id, entity_kind)`** retourne un `RemoteEntitySyncSnapshot`. Les tests utilisent des faux fournisseurs ; une application réelle brancherait HTTP, WebSocket, etc., **hors** de ce package.

## Conflits

**`SyncConflictDetector`** classe les situations en **`SyncConflictKind`** (ex. modification concurrente avec empreintes, tombeau distant vs travail local, divergence de version, parent différent, collision de clé métier externe).

**`SyncConflictResolutionStrategy`** (protocole) avec implémentations :

- priorité locale ;
- priorité distante (exige un instantané `present` sauf règles documentées) ;
- **manuel explicite** (`ConflictResolutionDecision` avec `requires_manual_resolution`).

**`InvalidSyncConflictResolutionException`** signale un contexte incohérent pour la stratégie choisie.

## Offline-first et journal

Le journal **`LocalMutationJournalPort`** complète la traçabilité des opérations à pousser. Il ne remplace pas les transitions sur les agrégats : les services métier continuent de faire évoluer les entités ; le journal enregistre des **événements** pour l’orchestrateur de synchro.

## Références code

- `application/sync_core_service.py`
- `application/sync_conflict_detector.py`
- `application/sync_conflict_resolution_service.py`
- `application/sync_conflict_resolution_strategy.py`
- `domain/sync_dtos.py`, `sync_conflict.py`, `sync_conflict_kind.py`
- `ports/remote_entity_sync_snapshot_port.py`
