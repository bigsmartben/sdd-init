# Native reviewed delivery

This repository-only integration starts from an **existing, locally created PR**.
It never creates a PR, marks a draft ready, uses Copilot CLI, approves workflows,
bypasses protection, or pushes directly to main. Read-only PR CI runs independently.

## Activation (not performed by this change)

The integration ships **disabled**. Its delivery job fails explicitly until activated;
green CI alone never authorizes delivery. First merge the reviewed workflow and helper
changes into main through an independently authorized path. `pull_request_target`
executes only that trusted base code and never checks out PR code with the user token.
An explicit Actions dispatch must select **main** and supply the existing PR number.
The workflow passes its event-time trusted commit as `CONTROLLER_SHA`. Initial
preflight requires both live main and the PR base to equal that commit; an old
queued controller cannot execute after main changes its delivery policy. This
initial binding is not reapplied after the run's own verified merge.

Before changing `.github/delivery.json` to `"enabled": true`:

1. Obtain authorization for billed reviews/cloud tasks, PR version commits, CI
   dispatches, merging, tags and GitHub Release publication. Configure an eligible
   Copilot license and repository policies. The current task-start REST API requires
   **Copilot Business or Enterprise** when repairs are needed. Review-only success
   does not call task-start. A readable task list does not prove start eligibility.
2. Add repository Actions secret **`SDD_DELIVERY_TOKEN`**, a fine-grained PAT or
   GitHub App **user access token**, scoped to this repository. Required permissions:
   **Agent tasks: read/write; Actions: read/write; Contents: read/write;
   Pull requests: read/write; Checks: read; Administration: read** (protection
   inspection), plus Metadata read. Do not use `GITHUB_TOKEN` or an installation
   token as a substitute. API authorization failures stop without mutation retries.
   The user must be allowed to request Copilot reviews and merge this PR; self-review
   and additional-human-approval rules remain GitHub's responsibility.
3. Configure **main branch protection**, enforced for administrators, with strict
   required status checks, at least one required approval, and no PR-review bypass
   allowances. Require these exact GitHub Actions contexts:
   `distribution-ubuntu-latest-py3.11`, `distribution-ubuntu-latest-py3.13`,
   `distribution-windows-latest-py3.13`. Use GitHub Actions as the expected check
   source. This implementation deliberately requires inspectable classic branch
   protection; it does not infer equivalent protection from an arbitrary ruleset.
   A GitHub plan supporting private-repository protection is essential for this
   path (separate from the Copilot subscription). The merge API has a head-SHA CAS,
   not a base-SHA CAS; strict, non-bypassable protection closes the base race.
4. Explicitly enable Copilot approving reviews. To let them satisfy required
   approvals, also enable **Allow Copilot approvals to count toward merge
   requirements**, with path scope covering the PR. Ordinary Comment reviews and
   approval prose are never accepted. Other required human approvals still apply.
5. Disable the repository's **Automatically delete head branches** setting before
   activation and keep it disabled throughout delivery. The preflight and final
   pre-merge guard reject `delete_branch_on_merge: true` (or an unreadable/missing
   value). No automatic repository-settings write is performed. Git and repository
   contents-write access must permit guarded remote branch deletion; branch rules
   still apply. The controller never deletes a local branch.
6. Keep **Require approval for workflow runs** enabled unless an administrator has
   separately authorized its documented risk. The integration waits for successful
   current-PR checks *before* dispatching additional candidate tests; missing,
   failed or approval-blocked checks do not cause an approval API call or fallback.
   Fully unattended continuation requires an explicitly authorized policy allowing
   those workflows, not a code workaround.
7. Permit merge commits and enable Actions. Keep `max_repairs` in `0..3` (default 2).
   This controller requests reviews through the native REST API. Before activating
   it, disable overlapping personal or repository automatic-review triggers for
   the same PRs; an already-pending native request returns 409 and deliberately
   stops the controller. Standalone automatic review is a separate mode while the
   controller is disabled. Server-side Native Automations and external model
   services are not required by this implementation.
8. If the old `delivery.yml` workflow was disabled during migration, keep it
   disabled until main contains the independently reviewed **new** controller and
   every activation requirement above is satisfied. Then explicitly re-enable
   that workflow. Replacing a workflow file does not itself establish that its
   disabled state was cleared; read the actual workflow state back before testing.

## Execution and failure boundaries

Opening a PR or marking it ready starts delivery. Subsequent `synchronize` events
run read-only PR CI, **not a fresh delivery loop**, so agent pushes cannot reset
the repair budget. Delivery uses one serialized concurrency group with `queue: max`:
up to 100 pending runs wait rather than replacing an older pending run. GitHub
cancels excess arrivals at capacity; it does not promise dispatch-time ordering.
A changed main/external head,
closed/draft/fork PR, active cloud task, exhausted budget, non-approved review,
failed CI, missing approval, denied API call or timeout stops delivery explicitly.
After inspection, an authorized maintainer can dispatch delivery for that PR;
that is an explicit new run with a new repair budget. Never blindly retry an
unknown task/merge/release outcome. Each poll phase is bounded to 120 x 15 seconds;
the job has a 180-minute outer timeout. Active cloud tasks are not cancelled or
restarted automatically when a workflow is interrupted.

The existing version helper chooses a patch increment or preserves an explicitly
higher stable version. Git object APIs prepare that version on the PR branch with
a non-force fast-forward update **before review**. Native tasks address inline
review findings on that existing branch; CI failures stop for investigation.
PR file lists are checked before automation and again before merging, including
both `filename` and `previous_filename` for renames. Root `.github/`, `.agents/`,
`.codex/`, `AGENTS.md`, the delivery/version/build/smoke helpers and delivery/version
gate tests are protected. These infrastructure PRs, including this bootstrap,
require independent/manual integration, not this automatic path.

After each native repair, the controller validates the actual old-to-new diff and
every repair commit's file list, so a protected change cannot be hidden by reverting
it later. Incomplete pagination, ambiguous rename origins and potentially truncated
comparisons stop for independent integration. The native task API does not provide
path-scoped write permissions: this is an enforced **acceptance/merge/release**
boundary, not a claim that a forbidden commit cannot appear on the PR branch. Such
a commit is rejected and left for manual inspection, never automatically reverted
or accepted on the strength of the prompt alone.
Every repaired head is reviewed again. Only an API-identified Copilot `APPROVED`
review for the exact current head can proceed. It must still pass GitHub's actual
merge requirements; no prose, empty finding count or bot mention grants approval.

GitHub supports checks against either the PR head or its synthetic test merge.
The controller validates the current test merge's parents, queries its check-runs
first, and falls back to the current head only when the test merge has no check-runs.
All required matrix checks must succeed on one exact source SHA; it never combines
partial test-merge results with green head results. Both head- and merge-attached
PR checks are covered offline. Dispatch-only checks are additional evidence, not a
substitute for GitHub's required PR checks or Actions approval policy.
The trusted main check workflow then tests the
exact synthetic merge. The merge API receives the expected head SHA and merge
method `merge`. Actual merge parents/tree and the platform PR record are verified.
The actual merged SHA is tested again before release. Only that run's exact
wheel/sdist/provenance artifact is used; GitHub artifact digest, source/version and
package hashes are verified. A new tag targets the merged SHA; a draft release gets
the tested packages, `PROVENANCE.json` and `SHA256SUMS`. Uploaded asset digests and
the tag are checked before publishing. Failed publication retains an inspectable
tag/draft; automatic resume/rollback is intentionally not attempted. Branch deletion
occurs only after verified publication and rechecking the actual merged PR identity.
The remote head is read first; a newer head is retained and cleanup is reported
blocked. An unchanged head is deleted using an explicit
`--force-with-lease=refs/heads/<branch>:<merged-pr-head>` and remote-only deletion
refspec, then absence is read back. A concurrent new commit rejects the lease.
An unsuccessful or timed-out Git command remains an unconfirmed outcome even if
the branch is subsequently absent; the receipt preserves that distinction and
stops for inspection rather than reporting a confirmed lease deletion.
There is no deletion through the REST API's unchecked DELETE endpoint. Git receives
credentials through its child environment, never URL/arguments/logs; raw Git output
is captured, credential helpers and local hooks are disabled. Failed/unknown cleanup
does not retry or undo the release: the receipt retains the published result plus
the cleanup blocker. Repository auto-delete is not used as an unchecked substitute.

`.build/delivery/receipt.json` and the Actions summary record actual review/task,
candidate/merged SHA, run, artifact and release identifiers, including partial
outcomes. No live integration/paid run is implied by offline tests.

## Current native API contracts

- [Agent tasks](https://docs.github.com/en/rest/agent-tasks/agent-tasks):
  `POST /agents/repos/{owner}/{repo}/tasks` accepts `base_ref`, `head_ref`,
  `create_pull_request: false`, `prompt`; the existing head branch is updated.
  Poll the returned task ID with GET; `waiting_for_user`, `idle`, failures and
  timeouts stop rather than pretending completion. User-to-server credentials only.
- [Copilot review](https://docs.github.com/en/rest/pulls/copilot-code-review):
  POST to `pulls/{number}/copilot-code-review` returns the requested review's
  **ReviewRequest** `node_id`, not a completed **PullRequestReview** ID. The receipt
  stores that request identity separately. After acceptance, the controller requires
  one new completed native Copilot review not present before the request, bound to
  the exact current head; multiple new reviews are ambiguous and block delivery.
  This does not claim a direct request-to-review ID mapping from the API.
  A pending request returns 409; eligibility/quota denials return 422.
  No automatic POST retries. [Review records](https://docs.github.com/en/rest/pulls/reviews)
  expose `is_copilot_code_review`, `node_id`, `commit_id` and structured `state`.
- [Workflow dispatch](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event):
  current API `2026-03-10` returns HTTP 200 with `workflow_run_id` and URLs.
  Missing run identity is blocked, not guessed by listing the latest green run.
- [PR merge](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request):
  `PUT pulls/{number}/merge` with `sha` performs head-SHA CAS. Protections remain
  mandatory; no direct reference update to main or admin override is used.
- [PR event SHA](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request)
  documents `GITHUB_SHA` as the test-merge SHA, distinct from `pull_request.head.sha`.
  [Required-check troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks#conflicts-between-head-commit-and-test-merge-commit)
  explicitly describes head versus test-merge check sources. The controller does not
  assume that every PR check-run's `head_sha` is the PR head.
- [Queued concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency#example-queueing-multiple-pending-runs)
  supports workflow-level `queue: max` with `cancel-in-progress: false`.
  [Git push lease](https://git-scm.com/docs/git-push#Documentation/git-push.txt---force-with-leaserefnameexpect)
  requires the remote reference to equal the explicit expected SHA, without relying
  on a possibly stale or background-updated local tracking branch.
- [Approval settings](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review#customizing-copilot-code-review),
  [workflow approval policy](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/configuring-agent-settings#allowing-github-actions-workflows-to-run-automatically-when-copilot-pushes),
  [optional server-side Automations](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations).
