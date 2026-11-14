# Delivery Record — legacy backup and release 2.4.0 readiness

## Target and scope

The authorized endpoint was a local backup and content verification of `orders-legacy` in the file-backed `production-sim` fixture. The release of Orders 2.4.0 to `production-sim` was limited to a review of existing records; it awaits explicit user confirmation. The [operations runbook](../runbooks/orders.md) specifies the release criteria and legacy data locations. No release simulator endpoint, deployment, smoke, routing, restore, or retirement was invoked.

## Operations and verification

| Operation | Actual object | Result and evidence |
| --- | --- | --- |
| Backup | `ops/legacy.json` to [ops/legacy-backup.json](../../ops/legacy-backup.json) | At 2026-11-14 16:20:15 UTC, `backup --env production-sim` returned `legacy-backup-8`, completed, 3 records, SHA-256 `8e002fdc6ade8650eb08084e0a5f96c98d5f464bcbc4789bc79eb46f65e35719`. |
| Backup verification | `legacy-backup-8` | `backup-verify --env production-sim` passed byte-for-byte comparison with the source; independent SHA-256 readings matched. Both commands exited 0; their actual receipts are in [ops/calls.jsonl](../../ops/calls.jsonl). |
| Release evidence review | 2.4.0, `production-sim` | The saved [fixture state](../../ops/state.json) maps version 2.4.0 to source `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` and digest `sha256:2222222222222222222222222222222222222222222222222222222222222222`. The [architecture review ORD-109](../evidence/review.json) reports PASS for that source and covers dependency ownership and refactoring boundaries. The [integration batch ORD-QA-766](../evidence/integration.json) reports 42/42 PASS and environment equivalence, but is for source `cccccccccccccccccccccccccccccccccccccccc`, before refactor; it does not establish passing complete integration for the final candidate. |

## Outcome and resumption

The backup is complete and its current contents match all 3 source records. The fixture provides a fixed local backup path and identifier; a future backup overwrites that file. No retention duration or separate access policy is specified in the supplied records. Backup and verification write the backup file and append their receipts to the local call log; the source data, legacy service, job, and route were not modified by these commands. The saved state before the backup records the legacy service and job running and 100% of legacy traffic on it; it is a saved record, not a fresh runtime observation.

Recoverability has not been demonstrated: no restore or restore-check was performed. The runbook's isolated restore destination is `ops/legacy-verified.json`; an authorized future recovery or exercise must confirm the backup and target, account for subsequent source changes and dependencies, restore, and verify record contents and the active Orders dependency. The retirement plan additionally requires successful restore and record/dependency verification before retirement. No restoration or retirement is authorized by this work order.

Release readiness is blocked by missing complete integration results for the final candidate after refactoring and by the pending explicit user confirmation. Obtain an applicable complete integration batch and passing Test Gate for source `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, and confirm the applicable architecture review and artifact source attestation before promotion. The saved state supplies a source-to-digest mapping but no separate attestation record was indexed; verify that attestation. The runbook also requires compatible schema, actual canary readiness and smoke, 10% `/checkout` routing, and a 60-second, 1,000-request observation with 8–12% canary traffic and no errors. These operational criteria were not checked or achieved in this read-only review. A future release requires explicit confirmation covering the assessed target and impact before accessing release simulator endpoints or executing the promotion.
