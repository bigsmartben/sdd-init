# Issue — <Stable ID and title>

Use sdd-documenter to maintain the lifecycle of one Issue from discovery, diagnosis, implementation, and verification evidence. Use the location specified in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). In existing projects, follow the index and update the authoritative record in place. Link the Issue from Test Reports and preserve historical records. Assign a stable, project-unique ID, include the record in handoffs, and reuse it across scenarios and batches. Create an Issue only when there is an issue to track.

## 1. Issue Facts

- **ID, title, and type** — <Implementation defect / Missing test / Evidence gap / Documentation conflict / Open requirement question>
- **Basis and affected scenarios** — <All related scenarios and ACs and the applicable requirements. Route a change to requirements through confirmation.>
- **Initial discovery** — <Time, discoverer, version, environment, and discovery report or test case link>
- **Reproduction** — <Preconditions, data, steps, and expected versus actual behavior. Link evidence in the report when available.>
- **Impact** — <Affected behavior and scope, with the basis for severity>

For a Bug handoff, reuse this Issue and its ID. Before handoff, record the behavior to restore, verified cause, impact, repair boundary (including behavior to preserve), passing criteria, and a runnable acceptance procedure or an accessible link to one. For a user-visible defect, use the original user action or public call entry point and give the preconditions, steps, observable expected results, and required regression checks. Explain equivalence if using a different scenario, and identify any criteria that require real integration and the conditions to run them.

For user-observable nonfunctional metrics, link the confirmed measurement conditions, statistical definition, and thresholds in the Issue's acceptance procedure or its referenced guide. Flag missing criteria before handoff.

Link the pre-fix diagnosis evidence in the Test Report separately from the acceptance procedure for the fixed version. The implementer owns the approach, file choices, Task breakdown, and local verification in the Plan.

## 2. Current Status

- **Assignee** — <Current assignee or Unassigned>
- **Fix Task** — <sdd-coder Plan or Task link. Use Not applicable for non-code work without a Task. The Plan holds the fix approach.>
- **Status** — <Pending / In progress / Fixed, awaiting retest / Closed after retest / Closed after verification / Blocked / Awaiting confirmation>
- **Blockers and resumption conditions** — <None or specific conditions>

Use [sdd-bugfix](../../skills/sdd-bugfix/SKILL.md) for assessment, diagnosis, and handoff. Use [sdd-coder](../references/delegation.md#实施交接) for the fix and its local checks. Route a separately requested local retest using [Responsibilities and Handoffs](../references/sdd-repository-governance.md#职责与交接). Link [sdd-test-loop](../../skills/sdd-test-loop/SKILL.md) evidence when the relevant original failure or regression is in the confirmed integration scope. Authorization for fixes, checks, and platform actions comes from the task.

## 3. Handling and Retest History

Append each handling or retest event and preserve the original discovery and each version. Link the corresponding Test Report for test steps and results.

| Time / Actor | Action and outcome | Fix version / Task / Local verification evidence | Retest report or case and version | Status change and basis |
|---|---|---|---|---|
| <Actual record> | <Fix, follow-up check, or verification> | <Reference or Not applicable> | <Verification evidence reference, remaining check, or Not applicable> | <Previous status, new status, and basis> |

Use Closed after retest when evidence on the fixed version covers the original or an equivalent scenario and required regression checks, with any required human confirmation recorded. Cite the local or integration evidence that satisfies those conditions. Use Fixed, awaiting retest when the fix is delivered and required checks remain. Missing or inconclusive evidence keeps the Issue awaiting retest or Blocked. When a retest fails, keep the original ID and new evidence and return to Pending or In progress at the appropriate stage. Use Closed after verification for a verified non-code Issue, and Awaiting confirmation when required human feedback is pending. If a closed Issue recurs, retain the closure history and record the reason for reopening.

## 4. Related References

<Link discovery and retest reports, relevant requirements, the Plan or Tasks, and any platform Issue. Platform actions require authorization under the task.>
