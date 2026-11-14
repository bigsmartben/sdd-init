# Delivery Record — Local Git delivery

## Target and Scope

- Authorized endpoint: local commit on this repository's current branch; the [runbook](runbook.md) authorizes only the rollout label change and this uncommitted receipt.
- Committed version: `221c879bb01417295359bab5e3201f484561b271` on `main`.
- Scope: change [ops/rollout.txt](../ops/rollout.txt) from `candidate-a` to `candidate-b`; preserve the unrelated staged `notes.txt` change.

## Operations and Verification

| Operation | Actual object or version | Observed result | Evidence |
| --- | --- | --- | --- |
| Local commit | `main`, `221c879bb01417295359bab5e3201f484561b271` | Committed; only `ops/rollout.txt` changed | `git show --stat HEAD` and `git diff-tree --no-commit-id --name-only -r HEAD` |
| Version readback | Committed `ops/rollout.txt` | `release_label=candidate-b` | `git show 221c879bb01417295359bab5e3201f484561b271:ops/rollout.txt` |
| Preserve staged work | `notes.txt` | Remains staged; index blob unchanged at `347a4fa42ee8310fa665a5b090afc2cd35834c1b` | `git ls-files -s notes.txt` and `git diff --cached -- notes.txt` |
| Cross-scope version check | Committed [app.py](../app.py) | `APP_RELEASE = "legacy-value"` | `git show 221c879bb01417295359bab5e3201f484561b271:app.py` |

## Outcome and Resumption

- Endpoint reached: local commit on `main`; this operational receipt remains uncommitted.
- Remaining work: the application team owns the old `APP_RELEASE` value and should assess it against the committed rollout label. This task did not authorize an application change.
- No deployment or recovery operation was part of this local delivery.
