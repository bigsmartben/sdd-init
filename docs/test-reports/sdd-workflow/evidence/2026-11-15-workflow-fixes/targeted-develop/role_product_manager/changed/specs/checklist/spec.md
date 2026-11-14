# Personal checklist

## Requirements

- FR-001 Add nonblank items and toggle completion independently.
- AC-001 Empty or whitespace-only input is rejected with a visible inline error without adding an item.
- AC-002 Text is trimmed and creates an unchecked item. With two items, checking and unchecking the first keeps the second unchecked.

## Requirements Prototype

- **Preview** — Open the local [personal checklist HTML](../../tests/prototypes/checklist/personal/index.html) in a browser. It is self-contained and needs no installation, server or credentials. This entry requires access to the project files; no externally hosted preview exists. External user access is pending verification.
- **Source and version** — `tests/prototypes/checklist/personal/index.html`, candidate v1, HTML SHA-256 `ae2c75c1f5034bb493f6acf9a68e871d81263dbf5707be0814cd924637fa1253`. The browser runner tested this exact source fingerprint on 2026-11-15.
- **Scope** — Medium-fidelity personal checklist for FR-001, AC-001 and AC-002: item entry, visible inline error, empty list, unchecked items, independently checked/unchecked items and completion count. All entries are simulated in page memory; reloading clears them. No storage service or product backend is connected.
- **Confirmation** — Candidate / Awaiting user operation and feedback. [Product decision](../../docs/confirmation.md) confirms behavior only, not this prototype's layout or experience. No user confirmation of candidate v1 has been received; the decision source supplies no confirmation date. Browser checks do not constitute user confirmation.
- **Supersession** — First candidate; no previously confirmed prototype is replaced.
- **Publishing prerequisite** — Main must select and authorize hosting and arrange the target environment, deployment access and intended viewer permissions. Publish the matching candidate version, then verify its external URL and user access before sharing it as an accessible hosted preview. This work order uses the local runner only, as directed in the product decision.

### Operation and verification

To review this candidate, open the local entry, submit an empty Item and then spaces, and check that each shows an inline error without creating a row. Add `  First item  ` and `Second item`; check that both start unchecked and the first label is trimmed. Check and uncheck the first item while observing that the second stays unchecked. Each checkbox can also be toggled directly. Reload to reset the memory-only demonstration. User feedback is still needed on this version's layout, interaction and visible states.

The sdd-product-manager role executed the project's [local browser runner](../../docs/preview.md), `run_prototype_check({})`, against the entry and SHA-256 above on 2026-11-15. Actual result: **Chromium 149.0.7827.55; process exit code 0**.

| Runner assertion | Applicable criterion | Actual result |
|---|---|---|
| `blank_rejection` | AC-001 | PASS |
| `trimmed_addition` | AC-002 | PASS |
| `independent_states` | AC-002 | PASS |
| `uncheck` | AC-002 | PASS |

These results cover the local HTML simulation only. Hosted access and user experience confirmation remain pending.
