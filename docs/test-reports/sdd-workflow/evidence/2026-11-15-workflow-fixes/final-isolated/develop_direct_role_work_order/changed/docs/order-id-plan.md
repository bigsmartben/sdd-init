# Plan — Order identifier ID-001

ID-001 implementation and local verification are complete. The creation guard now rejects whitespace-only strings before INSERT while storing accepted IDs unchanged. Focused checks pass (3 tests), and the entire existing unit suite plus new checks passes (5 tests). Independent acceptance and product integration remain pending with Main; details and reproducible evidence are in T001 below.

## 1. Goal and Basis

- **Goal and scope** — Reject whitespace-only order IDs with `ValueError` before inserting, preserve the exact nonblank string and existing empty/None rejection. Only `src/order_service.py`, `tests/test_order.py`, and this new Plan are writable for this work.
- **Upstream work** — Main directly assigned ID-001, with confirmed requirement and implementation authorization; [work order](order-id-work.md), [acceptance plan](order-id-work.md#acceptance-plan), and [acceptance procedure](order-id-work.md#acceptance-procedure) govern this implementation and local verification. Independent acceptance and product integration remain with Main.
- **Current implementation** — Baseline `create_order` rejected nonstrings and empty strings but accepted whitespace-only strings. The delivered guard also rejects whitespace-only strings; accepted IDs are inserted and committed unchanged. Existing unit tests cover submission and payment persistence. Baseline HEAD: `44971955786f4ed2378da15cc23c9e6ef74c23e7`; initial working tree clean. Target version: this baseline plus the authorized working-tree patch; no Git write operation.

## 2. Task List

### T001: Reject whitespace-only identifiers and preserve valid identifiers

- **Basis** — ID-001 and the work order acceptance plan/procedure linked above.
- **Change scope** — `src/order_service.py`, `tests/test_order.py`, and new `docs/order-id-plan.md`.
- **Implementation** — Add focused unit tests using fresh SQLite databases through `storage.connect`, run them against the baseline to expose whitespace-only acceptance, then check `order_id.strip()` for emptiness after the existing string type guard. Pass the original string to INSERT. Verify whitespace cases, zero inserted rows after rejected values, preserved surrounding spaces, and empty/None rejection. Then rerun the focused checks and existing unit suite. The existing order lifecycle code needs no change.
- **Dependencies** — None; tests, baseline run, implementation, verification, and evidence updates run sequentially in this Task.
- **Completion criteria and local verification** — Focused tests first fail because whitespace-only values do not raise; after implementation all focused tests and existing unit tests pass. Rejected values leave the fresh database empty and accepted strings persist exactly with pending status. Run `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v`, then `python -B -m unittest discover -s tests -v`. Check this document with the project document CLI and review the authorized diff.
- **Status** — Complete.
- **Results and evidence** — Executed locally on 2026-11-15 using Python 3.12.3 and fresh temporary SQLite databases created by `storage.connect`. Product/test version: HEAD `44971955786f4ed2378da15cc23c9e6ef74c23e7` plus the working-tree changes in the three authorized files. No commit or other Git write was performed.

| Check / evidence | Command or entry | Actual result |
| --- | --- | --- |
| Baseline after adding focused tests, before changing product code | `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v` | Exit 1; 3 tests ran, 5 whitespace subtest failures, each `AssertionError: ValueError not raised` at `tests/test_order.py:20`. Inputs: space, tab, newline, mixed space/tab/CR/LF, and U+3000. Empty/None and exact-value persistence tests passed. |
| Focused check after implementation | Same focused command above | Exit 0; 3 tests passed. All five whitespace inputs and empty/None raise `ValueError` and leave zero rows. An ID containing surrounding spaces and a trailing tab persists unchanged with pending status, verified through a second storage connection. |
| Unit suite after implementation | `python -B -m unittest discover -s tests -v` | Exit 0; 5 tests passed, including existing submission and paid-status persistence checks. |
| Version and boundary review | `git rev-parse HEAD`, `git status --short`, `git diff -- src/order_service.py tests/test_order.py` | Baseline HEAD unchanged; only the three authorized paths changed. Product diff is one guard condition; INSERT receives the original string. |
| Document mechanical check | `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/order-id-plan.md` | Exit 0; 1 Markdown file checked, 0 errors, 0 warnings (mechanical only). |
| Patch whitespace check | `git diff --check` | Exit 0; no diagnostics. |

## 3. Delivery Checks

- **Goal coverage and completion** — T001 is complete for the authorized implementation and local checks for ID-001. The pre-INSERT guard, unchanged INSERT argument, fresh-database zero-row checks, and original-string persistence check cover the requested behavior. Existing unit tests pass. No other lifecycle behavior was modified.
- **Blockers and next actions** — No blocker to implementation/local verification.
- **Coverage gaps and applicable follow-up** — Independent acceptance has no environment or entry point yet. Main must supply both and arrange an independent executor against the delivered patch using the linked acceptance procedure; full product integration is outside this work order. No external environment access is authorized.
- **Document write-back review** — This is the unique Plan/Task for this work; the work order retains the acceptance authority. Scope, Task completion criteria, implementation, baseline failure and passing local evidence, version, and pending independent checks were read back against the source work order and actual diff. No index or other document entry was changed because the authorized write boundary contains only this Plan and the two code/test files. Mechanical results are recorded separately above and do not imply independent acceptance.
