# Personal checklist

## Requirements

- FR-001 Add nonblank items and toggle completion independently.
- AC-001 Empty or whitespace-only input is rejected with a visible inline error without adding an item.
- AC-002 Text is trimmed and creates an unchecked item. With two items, checking and unchecking the first keeps the second unchecked.

## Requirements Prototype

- **Preview** — Open the local [Personal checklist HTML](../../tests/prototypes/checklist/personal/index.html) in a browser. It is self-contained and requires no installation or backend. The [local browser runner](../../docs/preview.md) verified this entry; external user access is not yet available or verified.
- **Source and version** — `tests/prototypes/checklist/personal/index.html`, candidate v1, identified by HTML SHA-256 `f9577d0f55837aff0740f89dc0a7201e8e3b652d6b485912aeedb59edb8031af`. This is the exact source fingerprint returned by the browser run, not a committed revision or hosted deployment.
- **Scope** — Medium-fidelity personal checklist for FR-001, AC-001 and AC-002: empty state, labeled Item input, Add action, visible inline invalid-input alert, unchecked new items, and independently toggleable completion states. The completion count and crossed-out completed text expose the current state. All data is simulated in page memory and is cleared on refresh; no product backend or persistence is used.
- **Confirmation** — **Candidate / Awaiting confirmation.** The [product decision](../../docs/confirmation.md) confirms behavior only; it explicitly leaves prototype operation and feedback pending. Recorded 2026-11-14; the source provides no separate confirmation date. Browser checks do not constitute user confirmation of this candidate's layout or experience.
- **Supersession** — Initial candidate; no previously confirmed prototype version exists in the project. Preserve a confirmed version's source and accessible entry when future candidates are introduced.
- **Operation and acceptance** — Open a fresh page; submit empty and whitespace-only input and check that an inline error appears with no new item (AC-001). Add a value with leading/trailing spaces and verify trimmed text and an unchecked checkbox. Add a second item; check and uncheck the first, verifying that the second remains unchecked (AC-002). Refresh to reset the simulated list.
- **Browser evidence** — Executed by `sdd-product-manager` on 2026-11-14 using `run_prototype_check` from this role's session, per the local runner instructions. Actual engine: Chromium; browser version: `149.0.7827.55`; process exit code: `0`. The tested HTML SHA-256 matches the source/version above. Runner results:

  | Check | Result | Applicable criterion |
  | --- | --- | --- |
  | `blank_rejection` | PASS | AC-001: invalid submission rejected visibly without an item |
  | `trimmed_addition` | PASS | AC-002: trimmed item added unchecked |
  | `independent_states` | PASS | AC-002: checking the first preserves the second's state |
  | `uncheck` | PASS | AC-002: unchecking the first preserves the second's state |

- **Publishing prerequisite** — Main must select and authorize hosting, arrange an externally reachable static preview and its user access permissions, and verify that the served HTML matches the recorded fingerprint before sharing it. No hosting was selected, authorized or deployed in this task. User operation and feedback remain required to confirm the candidate.
