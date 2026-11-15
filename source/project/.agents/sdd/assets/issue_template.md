# Issue — <Stable ID and title>

Maintain one Issue from discovery, diagnosis, implementation, and verification evidence. Use the location specified in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). In existing projects, follow the index and update the authoritative record in place. Link the Issue from Test Reports and preserve historical records. Assign a stable, project-unique ID, include the record in handoffs, and reuse it across scenarios and batches. Create an Issue only when there is an issue to track.

## 1. Issue Facts

- **ID, title, and type** — <Suspected defect / Implementation defect / Environment issue / Expected behavior / Missing test / Evidence gap / Documentation conflict / Open requirement question>
- **Basis and affected scenarios** — <Related scenarios, ACs, confirmed requirements, contracts, or prior behavior that applies. Record ambiguities and any required decisions.>
- **Initial discovery** — <Time, discoverer, version, environment, and discovery report or test case link>
- **Reproduction** — <Preconditions, data, steps, and expected versus actual behavior. Link evidence in the report when available.>
- **Impact** — <Affected behavior and scope, with the basis for severity>

For an integration finding, record the observed discrepancy and evidence. Include the Issue reference in the task receipt. When preparing or continuing a repair, keep the original ID and record the classification, evidence, and authorized stopping point. The repair work order records or links the behavior to restore, verified cause, impact, repair boundary (including behavior to preserve), and the [point-to-point acceptance plan and procedure](../references/sdd-repository-governance.md#验收计划与方案). Record the original user entry point for user-visible defects, the required regression checks, why any alternate scenario is equivalent, and any conditions that require real components.

For user-observable nonfunctional metrics, link the confirmed measurement conditions, statistical definition, and thresholds in the Issue's acceptance procedure or its referenced guide. List missing criteria and their impact in the receipt.

Link the pre-fix diagnosis evidence in the Test Report separately from the acceptance procedure for the fixed version. The implementer owns the approach, file choices, Task breakdown, and local verification in the Plan.

## 2. Current Status

- **Assignee** — <Current assignee or Unassigned>
- **Fix Task** — <Implementation Plan or Task link. Use Not applicable for non-code work without a Task. The Plan holds the fix approach.>
- **Status** — <Pending / In progress / Fixed, awaiting retest / Closed after retest / Closed after verification / Blocked / Awaiting confirmation>
- **Blockers and resumption conditions** — <None or specific conditions>

Link the assessment, diagnosis, implementation Task, local checks, and evidence for the original failure and required regression checks. Identify the actual fix version and any remaining check or user feedback. Authorization for fixes, checks, and platform actions comes from the task.

## 3. Handling and Retest History

Append each handling or retest event and preserve the original discovery and each version. Link the corresponding Test Report for test steps and results.

| Time / Actor | Action and outcome | Fix version / Task / Local verification evidence | Retest report or case and version | Status change and basis |
|---|---|---|---|---|
| <Actual record> | <Fix, follow-up check, or verification> | <Reference or Not applicable> | <Verification evidence reference, remaining check, or Not applicable> | <Previous status, new status, and basis> |

Use the [Issue closure rules](../references/sdd-repository-governance.md#issue-关单) to select the status and link the supporting evidence, affected criteria, required user feedback, and resumption conditions. On a failed retest, keep the original ID and new evidence and record whether diagnosis or implementation must resume. Use Closed after verification for a verified non-code Issue. If a closed Issue recurs, retain the closure history and record why it reopened.

## 4. Related References

<Link discovery and retest reports, relevant requirements, the Plan or Tasks, and any platform Issue. Platform actions require authorization under the task.>
