# Plan — Order identifier validation

## 1. Goal and Basis

- **Goal and scope** — Implement ID-001 in `src/order_service.py`, with focused checks in `tests/test_order.py` and execution evidence in this Plan. Reject whitespace-only IDs before insertion; preserve exact nonblank IDs and existing empty/None rejection. Other order behavior and external environments are outside this work order.
- **Upstream work** — [Confirmed work order and acceptance procedure](order-id-work.md). Main is the actual caller and receipt recipient.
- **Current implementation** — The baseline `create_order` rejected non-string and empty values but inserted whitespace-only strings. The completed patch additionally rejects whitespace-only values, retaining the original value for insertion. `storage.connect` initializes SQLite; existing order tests cover submit and paid persistence.

## 2. Task List

### T001: Reject whitespace-only order identifiers

- **Basis** — ID-001 and the [acceptance plan and procedure](order-id-work.md#acceptance-plan).
- **Change scope** — `src/order_service.py`, `tests/test_order.py`, and this new `docs/order-id-plan.md` only.
- **Implementation** — First add focused tests using a fresh temporary SQLite database through `storage.connect`. Cover whitespace-only rejection and zero rows, exact surrounding-space preservation, and empty/None rejection. Run these against the original implementation to demonstrate the missing validation, then use a stripped value only for the validation predicate and continue inserting the original ID. Run focused checks again and the existing unit suite.
- **Dependencies** — None.
- **Completion criteria and local verification** — Focused checks demonstrate the expected baseline failure, then pass after the change. Whitespace-only inputs raise `ValueError` with no inserted rows; nonblank IDs retain their exact value; empty/None rejection and existing order tests pass. Entry points: `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v` and `python -B -m unittest discover -s tests -v`.
- **Status** — Complete.
- **Results and evidence** — Local checks E1–E3 below cover every local criterion. Base commit `85d99c69365e679191df424839a826af2f07cfff`, plus the uncommitted patch in the three scoped files; the working tree was clean before this task. The implementation changes only the validation predicate to `not order_id.strip()` after the string-type check. The insert still receives the original `order_id`.

### Local execution evidence

Executed on 2026-11-15 in this isolated project root, using Python 3.12.3 and fresh temporary SQLite databases initialized by `storage.connect`; no external environment was accessed. This section is the retained local evidence, not an independent acceptance report.

| Evidence | Actual command and version | Actual outcome and coverage |
| --- | --- | --- |
| E1 — baseline | `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v`; base implementation plus new focused tests | Exit 1; 3 tests ran, 5 subtest failures. Space, tab, newline, mixed whitespace and U+2003 all reported `AssertionError: ValueError not raised`. Empty/None rejection and surrounding-space preservation passed. This confirms the original predicate admits whitespace-only strings. |
| E2 — fixed focused checks | Same focused command, after the implementation change | Exit 0; `Ran 3 tests`, `OK`. All 5 whitespace cases raise `ValueError` and leave zero rows. Empty/None also raise and leave zero rows. A separate SQLite connection reads the exact original nonblank ID, including surrounding spaces and a tab, with `pending` status. |
| E3 — regression | `python -B -m unittest discover -s tests -v`; same fixed version | Exit 0; `Ran 5 tests`, `OK`. Includes all focused tests and both pre-existing tests: normal submit and paid-state persistence. |
| E4 — patch hygiene | `git diff --check`; same fixed version | Exit 0; no diagnostics. |
| E5 — document mechanics | `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/order-id-plan.md` | Exit 0; 1 Markdown file checked, 0 errors and 0 warnings. This is mechanical checking only. |

Fixed executable asset SHA-256 values from `sha256sum src/order_service.py tests/test_order.py`:

```text
22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b  src/order_service.py
26381d93934fedd1954f2c34bff359f1820579e1a4e64e7629d98db4e867431f  tests/test_order.py
```

## 3. Delivery Checks

- **Goal coverage and completion** — T001 complete for implementation and local self-verification. E1 retains the expected original failure; E2–E3 establish rejection before insertion, exact-ID preservation, and regression coverage. No unrelated order behavior changed.
- **Blockers and next actions** — No local blockers or unresolved local failures. E5 records document mechanical checking. Semantic read-back of source, tests, scope and this Plan confirms that the work order, exact-ID exception, evidence and remaining independent check are preserved; no authority or acceptance status was broadened.
- **Coverage gaps and applicable follow-up** — Main will arrange the separate independent check required by the [acceptance plan](order-id-work.md#acceptance-plan). Its environment and entry point are still outstanding; this task grants no external access. Resume that check when Main supplies those inputs and the patch version.
