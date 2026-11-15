# Architecture Review Record — <Subject and batch>

> Record architecture conformance, remediation handoffs, architecture rechecks and behavior-preservation acceptance. Link the implementation Tasks and their Plan for the approach and local verification.

Use the location specified in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). Follow the project index for an existing record and maintain one record per review round. Link it from Status or Plan. This record serves as the report for architecture checks.

## 1. Scope and Context

- **Goal and scope** — <Engineering structure, modules, interfaces, dependencies, configuration, runtime assembly, and cross-module relationships. State exclusions and reasons.>
- **Architecture basis** — <Applicable project Code Review Rules and IDs, confirmed Blueprint or ARC, and relevant Interface Contract or Scenario Sequence clauses and versions. For an explicitly scoped technical debt item, include its technical target and the design constraints.>
- **Matrix and rule snapshot** — <Links plus immutable revision, hash or retained snapshot for the effective Review Matrix and project rules. Cite the matching Blueprint/contract version. Retain this batch's basis when the long-lived assets change.>
- **Asset validity and confirmation** — <Applicable mappings; confirmed initialization or affected updates and their confirmation reference. Pending decisions, stale entries and resumption conditions. Unchanged assets reuse prior confirmation.>
- **Review scope confirmation** — <The user's confirmed matrix entries, subjects, exclusions, implementation version and endpoint: review only, prepare remediation work orders, or implement and recheck. Cite existing explicit confirmation or record new/changed scope before initial review.>
- **Implementation snapshot** — <Git commit, relevant uncommitted changes, and artifact version>
- **Environment and reviewer** — <Environment, dependencies, data conditions, time, and reviewer. Cite the basis for any independence requirement.>
- **Remediation boundaries** — <Business logic and confirmed architecture to preserve, files or modules in scope, and authorized actions>
- **Behavior baseline for remediation** — <Confirmed criteria and their sources. Separately record pre-change version, environment, entry points, actual behavior, evidence and any differences. Link relevant conditions and thresholds for confirmed quality metrics.>

## 2. Review Checks and Follow-up

Select the batch's Review Tasks from the effective matrix according to the confirmed scope and change impact. Consider callers and read, write, dependency, and recovery paths. Use stable CHK IDs for task preparation, initial review, remediation and rechecks; keep implementation Tasks in their Plan. Do not infer a whole-matrix pass from selected coverage. Retain excluded, unchecked and affected stale/pending entries with reasons. Use PASS for conformance and exclude Not applicable from the pass count.

| Matrix entry | Rule ID | Batch coverage and rationale | Review Task / assignee |
|---|---|---|---|
| <RM ID> | <Project rule ID and design source> | <Selected / Excluded / Not applicable / Pending; reason, gap and resumption conditions> | <CHK ID and actual executor, or Not assigned> |

### CHK-001: <Subject and constraint>

- **Basis and subject** — <Matrix entry IDs, applicable rule IDs and design clauses, implementation locations, and cross-module paths>
- **Initial review assignment and procedure** — <Executor and caller, version, read/write boundaries, preconditions, method, observations and pass/violation criteria. Record Not run until the confirmed review scope permits execution.>
- **Acceptance plan** — <For each architecture recheck and applicable behavior-preservation check, record who is responsible, timing or preconditions, and any independence requirement.>
- **Architecture recheck procedure** — <Applicable constraint, subject and paths, preconditions, inspection or execution steps, observations, evidence and pass criteria.>
- **Initial review facts** — <Not run, or time, reviewer, snapshot, actual result, evidence, deviations, and impact. Use PASS / FAIL / UNVERIFIED / BLOCKED / Not applicable for the conclusion of a completed check.>
- **Refactoring work order** — <After initial review, use this check ID as the work order reference. Cite the matrix entry, rule, reviewed version and deviation evidence or authorized technical objective; specify the target, scope, affected locations, expected outcome, behavior to preserve, acceptance plan and procedures, assignee and authorized endpoint. Missing evidence requires investigation first. Use Not applicable if no change is needed.>
- **Behavior-preservation acceptance, when applicable** — <Link confirmed baseline criteria. Specify or reference the user entry point or public call, environment, data, steps, observations, evidence and pass criteria. Link the actual result on the remediation version, including covered criteria and any gaps.>
- **Implementation Tasks** — <Links to one or more Tasks in the Plan. A Task may address several checks. Recheck each check separately and keep the fix approach in the Plan.>
- **Current status and conclusion** — <Pending check / Conforming / Unfixed / Fix in progress / Fixed, awaiting recheck / Closed after recheck / Blocked. Use Not run while pending. Otherwise use PASS / FAIL / UNVERIFIED / BLOCKED / Not applicable. For a blocker, identify the specific problem, resumption conditions, and current assignee if known.>

| Batch / Time / Reviewer | Action or recheck scope and method | Snapshot, actual results, and evidence | Check conclusion and status |
|---|---|---|---|
| <Batch> | <Architecture recheck, behavior-preservation acceptance, or further investigation. Record scope and method.> | <Version, executor, actual result, and evidence. Link supporting Task evidence and state which criteria it covers.> | <Check conclusion and any remaining deviation.> |

Repeat this block for each check. Preserve the initial review and subsequent results. For investigation-only updates, record findings and recommendations. Use the original plan and procedures on the remediation snapshot. Close the item after its architecture recheck and applicable behavior-preservation acceptance pass. Return failures to the corresponding Task under the original check ID. Reuse evidence that still proves the criteria on the remediation snapshot and fill any gaps.

## 3. Gate and Remaining Work

- **Review Gate** — <Architecture recheck result, scope, and snapshot supported by the applicable checks>
- **Remaining work and next actions** — <Check IDs, specific problems, resumption conditions, and current assignees if known, or None>
- **Integration readiness after refactoring** — <Candidate version, affected paths, setup, entry points, and whether the authorized scenarios can run. List actual test prerequisites, blocked scenarios, and resumption conditions. Record open review and behavior items with their actual effect on testing. Link the integration Test Gate and formal release evidence separately when available.>
