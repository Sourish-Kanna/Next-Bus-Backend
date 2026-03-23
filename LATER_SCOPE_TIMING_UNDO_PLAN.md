# Later Scope Plan: Robust Timing Update/Delete/Undo

This file captures deferred work only.

## Status
- Phase: Later (not implemented)
- Code changes in this phase: None

## Goal
Evolve timing operations from aggregate-only updates into report-level operations that support exact undo and safe delete behavior.

## Why This Is Deferred
Current schema stores aggregate values per time slot (`deviation_sum`, `deviation_count`, `delay_by`) but does not keep per-report identity. Exact undo/delete of a specific report needs report-level data.

## Later Scope Items

1. Data model upgrade
- Add report-level tracking in each timing slot, for example:
  - `report_id`
  - `delay`
  - `reported_by`
  - `reported_at`
- Keep aggregate fields for fast read in app UI.

2. Operation log collection
- Add a separate operation log collection (example: `timingOperations`) to track:
  - action (`add`, `update`, `delete`, `undo`)
  - route
  - time slot
  - before/after snapshots
  - actor
  - timestamp
  - idempotency key
  - undone flag

3. Exact delete behavior
- Add delete-by-report-id endpoint.
- Recompute aggregate from remaining reports in that slot.
- If no reports remain, either keep zeroed slot or remove slot based on policy.

4. Exact undo behavior
- Add undo-last-operation endpoint (or undo-by-operation-id).
- Prevent double-undo using `undone` flag and idempotency checks.
- Restrict authorization for who can undo what.

5. Update endpoint refactor
- Update should append/modify report records first.
- Aggregate fields should be derived from report list to prevent drift.

6. Migration strategy
- Support legacy aggregate-only entries in compatibility mode.
- Optional backfill script for old data.
- Gradual migration by writing new format for new/updated entries.

7. Validation and testing
- Add tests for:
  - concurrent updates
  - repeated undo attempts
  - update/delete/undo consistency
  - legacy vs migrated slot behavior

## Risks to Address Later
- Race conditions when multiple users edit same slot.
- Historical consistency between route aggregate and historical data collections.
- Performance of aggregate recompute on high report volume.

## Out of Scope for Now
- No schema migration code.
- No new endpoint implementation.
- No behavior changes to existing `/v1/timings/update`.
