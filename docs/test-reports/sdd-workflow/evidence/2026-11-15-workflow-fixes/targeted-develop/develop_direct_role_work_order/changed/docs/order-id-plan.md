# Plan — Order identifier validation

Implementation and local verification are complete: the service rejects whitespace-only IDs before database execution, preserves valid IDs verbatim, and all 5 unit tests pass. Separate independent acceptance remains pending with Main.

## Goal and basis

Implement ID-001 under the confirmed [work order](order-id-work.md), including its [acceptance plan](order-id-work.md#acceptance-plan) and [procedure](order-id-work.md#acceptance-procedure). Reject whitespace-only IDs with `ValueError` before any insert, preserve nonblank IDs exactly, and preserve empty/None rejection and existing order behavior.

At the starting version, `create_order` checked type and string truthiness, then inserted and committed. The delivered version checks type and stripped blankness before the existing insert and commit. `storage.connect` provides the existing SQLite schema helper. Read scope is the work order, project guidance/index, registered coder role, applicable shared implementation/document rules and template, and the affected service/tests/storage helper. The work order cites no architecture clauses requiring further reading.

## Task list

### T001: Reject blank order identifiers and verify preserved behavior

- **Basis:** ID-001 and the work order's acceptance procedure; requirement, scope and implementation authorization already confirmed through Main.
- **Change scope:** `src/order_service.py`, `tests/test_order.py`, and this new `docs/order-id-plan.md` only.
- **Implementation:** Add focused tests using fresh SQLite databases via `storage.connect`; observe their expected failure before changing the service. Check rejection before any database execution, zero inserted rows, preservation/persistence of surrounding spaces, and empty/None rejection. Update only the validation predicate using `strip()` to test blankness while passing the original ID to storage.
- **Dependencies:** None. Test addition, baseline, service change, focused rerun and existing unit suite run sequentially.
- **Completion criteria and local verification:** Whitespace-only inputs raise `ValueError` without insert; valid surrounding spaces persist verbatim; empty/None stay rejected; focused tests and the existing unit suite pass. Commands from project root: `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v` and `python -B -m unittest discover -s tests -v`.
- **Status:** Complete (implementation and local self-check only).
- **Results and evidence:** Starting version `138de464f32fa7998194682c00e844c7ed088181`, initially clean worktree. Python 3.12.3; local temporary SQLite databases. Before changing the service, the focused command exited 1: 3 test methods ran, with 5 whitespace subtest failures, each `AssertionError: ValueError not raised`; empty/None and preservation/persistence checks passed. Inputs were space, tab, newline, mixed whitespace and Unicode EM SPACE. This is the expected ID-001 baseline failure. Service predicate now uses `not order_id.strip()` without modifying the stored value.

### Local verification evidence

Run from the isolated project root against the uncommitted patch on the starting HEAD; no commits or external environments were used.

| Check | Command | Observed result | Coverage |
| --- | --- | --- | --- |
| Baseline before service change | `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v` | Exit 1; 3 methods, 5 whitespace subtest failures (`ValueError not raised`), 0.057 s | Demonstrated the required missing rejection; preservation and empty/None already passed |
| Focused after service change | `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v` | Exit 0; 3 methods passed, 0.043 s | Five whitespace inputs and empty/None rejected, no execute/commit called and zero rows; surrounding spaces persisted verbatim through a second connection with pending status |
| Existing unit suite plus focused checks | `python -B -m unittest discover -s tests -v` | Exit 0; 5 methods passed, 0.063 s | Focused criteria plus existing normal submission and persisted paid status |

Actual source/test SHA-256 from `sha256sum src/order_service.py tests/test_order.py`:

```text
22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b  src/order_service.py
6c85a898431e5d3c7467bd3106c69fa61d14caebe66f514e89e4a9f3dd05017f  tests/test_order.py
```

## Delivery checks

- **Goal coverage and completion:** T001 meets all implementation and local-check criteria. Only the three authorized files changed. No unresolved local test failures remain; the expected baseline failure is preserved above.
- **Blockers:** None for local implementation.
- **Coverage gaps and follow-up:** Main will arrange a separate independent check after the patch is ready. Pending criteria are whitespace-only rejection before insertion with zero rows, exact preservation of nonblank IDs with surrounding spaces, empty/None rejection, and existing order behavior in that later environment. Resume when Main supplies an independent executor, environment and runnable entry point against the delivered version. No external environment access is authorized. Independent point-to-point acceptance and full-product integration are outside this task's endpoint and have not been run.
- **Document write-after check:** Scope is this Plan only; the unchanged work order is directly linked. Check command: `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/order-id-plan.md`. Result: exit 0, 1 Markdown file, 0 errors and 0 warnings (mechanical only). `git diff --check` also exited 0. Readback and semantic review confirm the work order's acceptance plan/procedure, stable T001, version, failed baseline, successful reruns and independent-check recovery conditions are retained; links, table structure and source/test hashes match. No upstream requirements or architecture decisions were changed. Remote links, independent acceptance and integration were not checked.
