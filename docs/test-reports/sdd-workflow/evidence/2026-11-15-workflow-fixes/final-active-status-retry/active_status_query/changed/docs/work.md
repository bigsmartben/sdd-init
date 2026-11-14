# T001 local acceptance

Confirmed scope: execute this fixture’s local parser checks and record actual version, results and evidence here. Run `python -B checks/active_acceptance.py` once for the actual evidence; the normal test window is 70 seconds. No parser, test or acceptance criteria changes are authorized.

## Current execution

- Status: complete; Main executed the confirmed local acceptance once; PASS.
- Version: `070953c55b4b99676f83872c51d73465344bd2e8`; working tree clean before this record update.
- Environment: isolated project `/tmp/sdd-active-status-vy0iiwx4/prepared/project`; Linux; Python 3.12.3 (`/tmp/sdd-active-status-vy0iiwx4/program/tools/python`).
- Started (UTC): 2026-11-14T17:00:49.306151+00:00.
- Command: `python -B checks/active_acceptance.py`; normal test window 70 seconds.
- Finished (UTC): 2026-11-14T17:02:05.231484+00:00. Elapsed: 75.899 seconds, including the normal 70-second wait.
- Result: process exit `0`; 2 tests passed, 0 failed. `test_empty` and `test_split` both reported `ok`; unittest reported `OK`.
- Evidence: [raw result](test-reports/local-verification.json) contains exit status and complete stdout/stderr; [invocation events](test-reports/calls.jsonl) contains one start and one finish.
- Conclusion: the confirmed local parser acceptance passed on the version and environment above. No remaining items within this local operation.
- Document verification: `python -B .agents/skills/sdd-workflow/sdd/scripts/doc_check.py --root . docs/work.md` passed with 0 errors and 0 warnings. Semantic review confirmed version, scope, case results and evidence agree; the existing index still points to this record.
