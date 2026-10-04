# Production verification

Use this reference only for the applicable branch below. Record its contract and evidence in the PRD, not a second operations document. Merge completion is not production release readiness.

## Telemetry

Applies when approved work changes I/O, retries, jobs, external calls, or telemetry and operational diagnosis is a requirement. A local tool without that requirement needs no telemetry setup.

- Name the on-call questions first. Map each to an existing log, metric, or trace, its owner, and the exact query or check that answers it. Reuse the project's logger and telemetry stack.
- Preserve correlation/run IDs and, when entry points share a sink, entry-point attribution. Use bounded metric labels; request IDs, user IDs, and free text belong outside metric labels. Allowlist emitted fields and omit secrets and unnecessary personal data.
- Induce a controlled error only in an authorised safe test environment. Capture the real emitted artifact, locate the failure by correlation/run ID, and check attribution and private-field exclusion. A unit assertion about logger calls alone is not this evidence.
- If alert changes are in scope, verify the alert, recipient, and runbook in that safe environment. Distributed tracing is needed only when the approved diagnostic question crosses services; other questions can use existing local signals.

## Migration

Applies when persistent schemas, backfills, or external consumers must remain compatible across deployment stages.

- Name the database engine/version and each schema stage. Check old/new readers and writers against every stage in which they run, not only the final new-code/new-schema pair. Include external consumers.
- Where versions overlap, use additive expansion, verified backfill/caller migration, cutover, and destructive contraction last. Require evidence that old readers and writers are retired before dropping their contract. An index or nullable-column addition is not universally safe: check engine-specific locking, transaction behaviour, table size, and resource limits.
- For each backfill, specify checkpoints, retries, idempotency, completeness verification, batch/lock bounds, and safe interruption/resumption. Replay representative fixture data and check partial and repeated runs.
- Separate code rollback from schema/data recovery. Verify the recovery procedure with representative fixture data. Reverting code does not restore removed data. If reversal is destructive or unavailable, label the change a one-way door and specify tested backup/restore or forward recovery; missing recovery evidence remains a blocker.

## Evidence

- For each applicable requirement, record source revision plus dirty-state/input hashes when needed, command/query, artifact location, expected observation, actual observation, and grade: `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`.
- Mark a non-applicable branch with a short reason. Keep required acceptance criteria and slices open when evidence is missing or inconclusive, and name the missing access or artifact.
- Missing safe-environment access is a blocker, not permission to use production, trigger a real alert, or invent a pass. Follow the calling phase's existing approval and scope rules.
