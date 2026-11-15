# Plan — Reject whitespace-only order IDs

T001 is complete: ID-001 validation is implemented, focused checks pass (3 tests), and the complete existing unit entry passes (5 tests, including the 2 original tests). Independent checking remains pending with Main.

## 1. Goal and Basis

- **Goal and scope** — Implement ID-001 within `src/order_service.py` and `tests/test_order.py`; maintain this Plan. Reject whitespace-only IDs before insertion, preserve nonblank IDs exactly, and retain empty-string and None rejection. No other order behavior changes.
- **Upstream work** — [Issued work order](order-id-work.md), including its [acceptance plan](order-id-work.md#acceptance-plan) and [acceptance procedure](order-id-work.md#acceptance-procedure). Main has confirmed requirements, scope and implementation authorization.
- **Implementation baseline and result** — Before this change, `create_order` rejected nonstrings and empty strings but allowed whitespace-only strings to reach insertion. The completed implementation rejects strings whose stripped value is empty before inserting and committing the original nonblank ID. `storage.connect` supplies the SQLite schema used by tests.

## 2. Task List

### T001: Enforce ID-001 and verify local behavior

- **Basis** — ID-001 and the work order acceptance procedure above.
- **Change scope** — `src/order_service.py`, `tests/test_order.py`, and this new `docs/order-id-plan.md`.
- **Implementation** — Add focused tests first using a fresh SQLite database from `storage.connect` for each test/input. Assert whitespace-only IDs raise ValueError with zero rows; assert a nonblank ID with surrounding spaces is stored verbatim; assert empty and None remain rejected with zero rows. Observe baseline failure, then use a stripped value only for the validation predicate while inserting the original ID. Run focused tests and the existing unit suite.
- **Dependencies** — None. Test addition, baseline run, implementation and verification execute sequentially because they share files and establish the regression evidence.
- **Completion criteria and local verification** — All four work-order behaviors pass, including zero insertion for rejected inputs, and the existing unit suite passes. Focused entry: `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v`. Full unit entry: `python -B -m unittest discover -s tests -v`. These are implementation self-checks only.
- **Status** — Complete.
- **Results and evidence** — Starting and current HEAD: `07f49ab83406c7ac7d1c33d0d24c78ffa276825b`; clean starting worktree in the isolated project supplied by Main. After adding tests but before modifying product code, the focused command above exited 1: `Ran 3 tests`, `FAILED (failures=5)`. Each whitespace-only input (`" "`, `"\t"`, `"\n"`, `" \t\r\n "`, `"\u2003"`) failed at `assertRaises(ValueError)` with `AssertionError: ValueError not raised`; surrounding-space preservation and empty/None rejection passed. The baseline therefore establishes the expected validation gap; zero-row assertions for the failing inputs are reached only after the implementation is fixed. Implementation now validates `order_id.strip()` without replacing the value passed to INSERT.

#### Local verification evidence

Executed in `/tmp/sdd-review-execution-c1a1xm_t/develop_direct_role_work_order-9m3px8v6/prepared/project` on 2026-11-14 with Python 3.12.3 and SQLite 3.45.1. SQLite databases are temporary files freshly created with `storage.connect` for each focused input; cleanup closes connections before removing directories. No external environment was accessed.

| Entry | Result | Coverage |
| --- | --- | --- |
| `python -B -m unittest discover -s tests -p test_order.py -k OrderIdentifierTests -v` before implementation | Exit 1; 3 tests, 5 failing subtests; `ValueError not raised` | Expected whitespace validation gap; empty/None rejection and original-value preservation already pass |
| Same focused command after implementation | Exit 0; `Ran 3 tests in 0.061s`, `OK` | Five whitespace variants raise ValueError with zero rows; empty and None raise ValueError with zero rows; `"  ORDER-2 \t"` stored exactly with pending status |
| `python -B -m unittest discover -s tests -v` after implementation | Exit 0; `Ran 5 tests in 0.086s`, `OK` | All focused tests plus both original submit and paid-status persistence tests |
| `git diff --check` | Exit 0; no diagnostics | Patch whitespace |

The final worktree has only `src/order_service.py` and `tests/test_order.py` modified, plus this new Plan; no commit or Git configuration/index mutation was performed.

Tested product/test file identities from `sha256sum src/order_service.py tests/test_order.py`:

- `src/order_service.py`: `22dfe4f33d3a018f3d50ca8518202367e3206fd68a098d4edbb6570a651d6f3b`
- `tests/test_order.py`: `86101c3b156edbc3218f9d6261a5fe029d697937195901f44491de2aac1902e4`

## 3. Delivery Checks

- **Goal coverage and completion** — T001 meets every implementation/local-self-check criterion: pre-insert rejection of pure whitespace, unchanged stored nonblank IDs, retained empty/None rejection and original unit regression coverage. Rejection before the INSERT is also evident directly from the validation branch in `create_order`.
- **Blockers and next actions** — No implementation blocker or unresolved local failure. Deliver the uncommitted patch and this Plan to Main.
- **Coverage gaps and applicable follow-up** — Main owns the separate independent check under the upstream acceptance plan. Each criterion remains independently pending there: whitespace ValueError/zero insertion; exact surrounding-space preservation; empty/None rejection; existing unit regression. Known preparation: reproduce this patch over the recorded HEAD, use Python with standard-library SQLite, and use fresh databases from `storage.connect`. The focused/unit commands above are runnable local evidence entries; Main must supply the independent environment and entry point. No point-to-point acceptance, full-product integration or architecture Review was executed or concluded by this Task.
- **Document checks** — This Plan is the sole new evidence record; no upstream document or index changes are needed. `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/order-id-plan.md` exited 0: `Checked 1 Markdown files: 0 errors, 0 warnings (mechanical only)`. Readback against the work order and diff confirms scope and criteria, stable T001, baseline failure, passing local evidence and pending independent check remain distinct and accurately linked. No remote links or external environments were checked; mechanical success is not independent acceptance.
