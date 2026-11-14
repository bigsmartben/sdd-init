# Architecture Review Record — <Subject and batch>

> sdd-documenter records the initial review, sdd-coder handoff, and recheck results from their respective executors. Use this record to assess architecture conformance and application of Code Review Rules. sdd-coder develops and maintains the fix approach in the Plan. Link the Task from this record.

Use the location specified in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). Follow the project index for an existing record and maintain one record per review round. Link it from Status or Plan. This record serves as the report for architecture checks.

## 1. Scope and Context

- **Goal and scope** — <Engineering structure, modules, interfaces, dependencies, configuration, runtime assembly, and cross-module relationships. State exclusions and reasons.>
- **Architecture basis** — <Project Code Review Rules path and rule IDs, Blueprint or ARC, and relevant Interface Contract or Scenario Sequence clauses and versions>
- **Rule validity and maintenance notice** — <Validity and mapping for the affected design, with reasons for reusing prior checks. For missing or outdated rules, list the design clauses, rule IDs, scope still to check, and the need to create or update rules. The user decides when to maintain the rules.>
- **Implementation snapshot** — <Git commit, relevant uncommitted changes, and artifact version>
- **Environment and reviewer** — <Environment, dependencies, data conditions, time, and reviewer. Cite the basis for any independence requirement.>
- **Remediation boundaries** — <Business logic and confirmed architecture to preserve, files or modules in scope, and authorized actions>

## 2. Review Checks and Follow-up

Select checks based on the impact of the change and each rule's applicability. Consider callers and read, write, dependency, and recovery paths. Assign stable IDs to all applicable checks. Retain unchecked items and scope affected by missing or outdated rules as pending checks. Record each check's initial findings, actions, and rechecks in its own section. Use PASS for conformance and exclude Not applicable from the pass count.

| Rule ID | Applicability | Rationale and source | Check |
|---|---|---|---|
| <CRR ID or engineering structure clause> | <Applicable / Not applicable / Pending check> | <Rationale and source. Link the check for detailed evidence. For pending checks, record the gap and resumption conditions and use UNVERIFIED.> | <CHK ID / Not applicable / Pending check> |

### CHK-001: <Subject and constraint>

- **Basis and subject** — <Applicable rule IDs and design clauses, implementation locations, and cross-module paths>
- **Check method and expectations** — <Before dispatch, sdd-review-code defines the developer-facing acceptance plan: constraint, subject and paths to inspect, conditions, reproducible inspection or execution method, evidence to collect, and pass criteria.>
- **Initial review facts** — <Not run, or time, reviewer, snapshot, actual result, evidence, deviations, and impact. Use PASS / FAIL / UNVERIFIED / BLOCKED / Not applicable for the conclusion of a completed check.>
- **Remediation handoff** — <Use this check ID as the work order reference. Cite the rule and deviation evidence above. Record the remediation target, scope and implementation locations, expected outcome, behavior to preserve, recheck plan in this check, and assignee. Record dispatch time or status. Use Not applicable if no fix is required or only more investigation is needed.>
- **User acceptance, when applicable** — <Before dispatch, link the user-facing plan and criteria separately from the architecture recheck and identify the executor. Keep the result pending until evidence is available, then link it here.>
- **Implementation Tasks** — <Links to one or more Tasks in the Plan. A Task may address several checks. Recheck each check separately and keep the fix approach in the Plan.>
- **Current status and conclusion** — <Pending check / Conforming / Unfixed / Fix in progress / Fixed, awaiting recheck / Closed after recheck / Blocked. Use Not run while pending. Otherwise use PASS / FAIL / UNVERIFIED / BLOCKED / Not applicable. For a blocker, identify the specific problem, assignee, and resumption conditions.>

| Batch / Time / Reviewer | Action or recheck scope and method | Snapshot, actual results, and evidence | Check conclusion and status |
|---|---|---|---|
| <Batch> | <Further investigation or recheck. Include the original deviation, affected rules, and cross-module relationships.> | <Version, recheck evidence, and evidence that business behavior is preserved. Link the Task and any integration evidence needed by the check.> | <Check conclusion. Continue remediation if the recheck fails.> |

Repeat this block for each check. Preserve the initial review and subsequent results. For investigation-only updates, record the investigation. The original reviewer applies the check plan to the remediation snapshot and closes the check after a passing recheck. If the recheck fails, send it back to the corresponding Task under the original check ID. Reuse unaffected evidence when the impact analysis explains why it applies to the current snapshot.

## 3. Gate and Remaining Work

- **Review Gate** — <Summary, scope, and snapshot provided by the reviewer under sdd-review-code criteria>
- **Remaining work and next actions** — <Check IDs, assignees, specific problems, and resumption conditions, or None>
