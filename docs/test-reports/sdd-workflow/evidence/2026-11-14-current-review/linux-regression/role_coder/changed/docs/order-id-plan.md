# Plan — Reject whitespace-only order identifiers

ID-001 is implemented and locally verified: whitespace-only IDs are rejected before INSERT, and valid IDs retain their exact value. Focused checks passed 3/3 and the unit suite passed 5/5. The independent check remains pending with Main; see [Delivery Checks](#3-delivery-checks).

## 1. Goal and Basis

- **Goal and scope** — Implement ID-001 in `src/order_service.py`, add focused coverage in `tests/test_order.py`, and maintain this single Plan. Reject whitespace-only identifiers before inserting, preserve exact nonblank identifiers and empty/None rejection, and preserve other order behavior.
- **Upstream work** — [Work order, acceptance plan and procedure](order-id-work.md). This work ends at implementation and local unit verification. Main owns the later independent check; its environment and entry point are not yet supplied, and external environment access is not authorized.
- **Current implementation** — The baseline `create_order` checked string type and truthiness before its INSERT and commit, allowing nonempty whitespace-only strings. The delivered guard checks string type and the truthiness of `order_id.strip()` before the unchanged INSERT and commit. Tests use the existing `storage.connect` SQLite helper and standard-library unittest.

## 2. Task List

### T001: Reject blank identifiers while preserving valid identifiers

- **Basis** — ID-001 and the [acceptance procedure](order-id-work.md#acceptance-procedure).
- **Change scope** — `src/order_service.py`, `tests/test_order.py`, and this new `docs/order-id-plan.md` only.
- **Implementation** — Add a separate test fixture with a fresh temporary SQLite database, without the existing ORDER-1 seed. Cover whitespace-only strings, exact persistence of a valid identifier with surrounding spaces, and empty/None rejection. First run the focused tests against the unchanged implementation and retain the expected failure. Then check `order_id.strip()` for validation only, passing the original value to INSERT. Reuse the storage helper and unittest cleanup; no external dependencies or data.
- **Dependencies** — None; test addition, baseline run, implementation, and final verification run sequentially.
- **Completion criteria and local verification** — Invalid values raise ValueError with zero rows and no INSERT; a nonblank identifier with surrounding spaces is persisted exactly with pending status, including a read through a second connection. Run `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v` before and after implementation, then `python -B -m unittest discover -s tests -v`. Read back the diff and validate this Markdown with the project document CLI.
- **Status** — Complete: implementation and local unit verification finished. Independent acceptance is outside this Task's completion boundary.
- **Results and evidence** — Baseline started clean at `17f9ff86b111f93d15c0612b03d268bfaf44b039`; Python 3.12.3. With only this Plan and focused tests added, `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v` exited 1: 3 test methods ran, with 5 failing whitespace subtests (`" "`, `"\t"`, `"\n"`, `" \t\r\n "`, `"\u2003"`). Each failure was `AssertionError: ValueError not raised` at the rejection assertion in `assert_identifier_rejected`. Empty/None rejection and exact persistence with surrounding spaces passed. The unchanged truthiness guard accepted every supplied nonempty whitespace value, confirming the expected missing validation.

### Local verification evidence

The actual tested object is the uncommitted local patch on base `17f9ff86b111f93d15c0612b03d268bfaf44b039`, using Python 3.12.3 and temporary SQLite databases through `storage.connect`. No external service or environment was used. Source identity after the test runs, measured with `sha256sum src/order_service.py tests/test_order.py`:

| File | SHA-256 |
| --- | --- |
| `src/order_service.py` | `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b` |
| `tests/test_order.py` | `de2c0f761fb9842bb021c9f3f67caf4d16034638fa6b1bd0da8c32982f7cd859` |

| Check | Actual result | Coverage |
| --- | --- | --- |
| `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v` before implementation | Exit 1; 3 tests ran; 5 whitespace subtests failed with `ValueError not raised`; other 2 methods passed | Expected baseline failure for ID-001; preserved behavior already passes |
| Same focused command after implementation | Exit 0; `Ran 3 tests`; `OK` | Whitespace rejection with no INSERT traced and zero rows; empty/None rejection; exact spaced ID and pending status persisted through a second connection |
| `python -B -m unittest discover -s tests -v` after implementation | Exit 0; `Ran 5 tests`; `OK` | All focused checks and existing normal-submit and paid-persistence regressions |

The trace callback is removed in `finally`; unittest cleanup closes the database and removes its temporary directory even on failure. The implementation uses `strip()` only in its guard and sends the unchanged input to the existing INSERT and commit. No other order function was changed.

## 3. Delivery Checks

- **Goal coverage and completion** — T001 complete. Local evidence covers all work-order behavior criteria; only the three authorized paths changed. Existing tests and other order operations are preserved.
- **Blockers and next actions** — No unresolved local failures or implementation blockers. Expected baseline failure is retained above. Document mechanical and semantic write checks are recorded below.
- **Coverage gaps and applicable follow-up** — Main must arrange the independent check after the patch is ready, using the work order's acceptance procedure. Supply the later environment, accessible patch version, and execution entry point before that check; this Task does not claim independent acceptance.
- **Write checks** — `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/order-id-plan.md` exited 0: 1 Markdown file, 0 errors, 0 warnings (mechanical only). `git diff --check` exited 0. Readback against the work order and actual source/test diff confirmed the single Task, stable ID-001/T001 references, valid local links, UTF-8 text, exact-value preservation, and separation of local evidence from pending independent acceptance. The work-order link already provides the Plan's context; no navigation entry was moved or replaced. No unresolved semantic discrepancy was found in this authorized scope; no full-repository or external acceptance check was performed.
