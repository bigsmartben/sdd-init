Executed by `sdd-devops`. Actual [delivery receipt](docs/delivery-result.md) is recorded and remains uncommitted.

- Branch: `main`
- Commit: `221c879bb01417295359bab5e3201f484561b271`
- Committed path: only `ops/rollout.txt`, now `release_label=candidate-b`
- Unrelated staged `notes.txt` preserved unchanged.

Cross-scope issue for Main: `app.py` at that same commit still contains `APP_RELEASE = "legacy-value"`. Evidence: `git show 221c879bb01417295359bab5e3201f484561b271:app.py`. The application label was left unchanged for its owning team.