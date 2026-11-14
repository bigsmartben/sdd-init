# Personal checklist

## Requirements

- FR-001 Add nonblank items and toggle completion independently.
- AC-001 Empty or whitespace-only input is rejected with a visible inline error without adding an item.
- AC-002 Text is trimmed and creates an unchecked item. With two items, checking and unchecking the first keeps the second unchecked.

## Prototype Reference

- **Preview** — Open [the local HTML entry](../../tests/prototypes/checklist/personal/index.html) in a browser on a machine with this project checkout. It is self-contained and needs no server or dependencies. The local runner accessed this file successfully; access from an end user's device remains unverified. No externally hosted preview exists.
- **Source and version** — [tests/prototypes/checklist/personal/index.html](../../tests/prototypes/checklist/personal/index.html), candidate v1, SHA-256 `d401df9dc918a0384b0df96152f3d240c3343eb4f307239cf963ce664f739e75`. This content fingerprint identifies the exact HTML exercised below; verify it before reusing these results.
- **Scope** — Medium-fidelity personal checklist covering FR-001, AC-001 and AC-002: empty state, Item input and Add action, visible inline invalid-input alert, trimmed unchecked additions, and independently checkable/uncheckable rows. All data is simulated in browser page memory; refreshing resets it. No backend, persistence or product write interface is used.
- **Confirmation** — **Candidate / Awaiting confirmation.** [The product decision](../../docs/confirmation.md) confirms behavior only. Automated operation on 2026-11-15 does not establish user confirmation of this prototype's layout or interaction experience. User operation and feedback on candidate v1 remain pending.
- **Supersession** — Initial candidate; there is no previously confirmed prototype to supersede.
- **Operation for feedback** — Open the entry, submit empty or whitespace-only text and observe the inline error with no item added. Add `  First item  ` and then `Second item`; observe two unchecked rows and trimmed text. Check and uncheck the first row; the second remains unchecked. Give feedback on the layout, input/error experience and completion states, citing candidate v1.
- **Browser evidence** — Executed by `sdd-product-manager` on 2026-11-15 using the project's [local runner](../../docs/preview.md), tool `run_prototype_check`, against the HTML fingerprint above. Actual Chromium version `149.0.7827.55`; process exit code `0`. The runner returned:

  | Check | Result | Applicable criterion |
  |---|---|---|
  | `blank_rejection` | PASS | AC-001: blank input creates no item and displays the alert |
  | `trimmed_addition` | PASS | AC-002: trimmed text creates an unchecked item |
  | `independent_states` | PASS | AC-002: checking the first item leaves the second unchecked |
  | `uncheck` | PASS | AC-002: unchecking the first leaves the second unchecked |

- **Publishing prerequisite** — Main must select and authorize an external preview host, arrange deployment permissions and the intended audience's access, then publish this version and verify its URL and matching source fingerprint from the intended user context. The current task authorizes only the local runner; external publishing and user access verification are pending.
