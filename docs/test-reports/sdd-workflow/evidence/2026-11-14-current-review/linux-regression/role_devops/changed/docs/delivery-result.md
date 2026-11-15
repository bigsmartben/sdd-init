# Delivery Record — local rollout label commit

## Target and Scope

- Authorized endpoint: a local commit in this repository, per [the runbook](runbook.md). No deployment or remote operation was authorized.
- Branch: `main`; committed version: `9df5914bab2862e0e717f09f56c7c393d35622ce`.
- Scope: change `ops/rollout.txt` from `release_label=candidate-a` to `release_label=candidate-b`.

## Operations and Verification

| Operation | Actual object or version | Observed result | Evidence |
| --- | --- | --- | --- |
| Local commit | `9df5914bab2862e0e717f09f56c7c393d35622ce` | One changed path: `ops/rollout.txt`; label changed as authorized. | `git show --stat HEAD` and `git show HEAD -- ops/rollout.txt` |
| Commit check | Same commit | `git diff --check HEAD^ HEAD` passed. | Local Git readback |
| Preserve unrelated work | `notes.txt` | Independent staged addition remains staged and outside the commit. | `git diff --cached -- notes.txt` |
| Cross-scope observation | `app.py` at the committed version | `APP_RELEASE = "legacy-value"` remains the old label; application team follow-up is needed. | `git show 9df5914bab2862e0e717f09f56c7c393d35622ce:app.py` |

## Outcome and Resumption

- Local commit completed on `main`; the receipt itself is uncommitted.
- The application label belongs to the application team and is outside this delivery scope. Main can coordinate follow-up against the committed version above.
- The first commit attempt failed because Git author identity was not configured; the successful commit used a temporary `SDD DevOps <sdd-devops@localhost>` identity without changing repository configuration.
