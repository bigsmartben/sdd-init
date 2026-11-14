# Test Report — <Subject and batch>

Complete this report from the confirmed goals, scope and criteria, the preparation for the run, and the actual evidence. Identify whether the run was requirements acceptance, integration verification, local verification by the implementer, feasibility verification, Bug diagnosis, or a retest. Use the [Architecture Review Record template](review_template.md) for architecture conformance.

Use the location specified in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). Follow the existing project index. For a simple or local task, record the applicable facts in the current task record. Preserve historical paths and versions.

Use the full structure for integration regression. A simple or local task may use a concise entry with the purpose and criteria, actual version and environment, cases and results, evidence links, and any gaps, impact and resumption conditions. Add human feedback and relevant Issue or prior-run references when applicable. In either form, reuse precise references for applicable plans, guides and cases, identify deviations and retain failed attempts. Adjust links for the record's actual location.

## 1. Test Goals and Basis

- **Batch, verification type, executor, and time** — <Actual details>
- **Subject and goal** — <Capability, module, or candidate approach and what this run aims to establish>
- **Basis** — <Spec scenarios or ACs, confirmed engineering goals, the Quickstart used for full functional integration regression or the work order's acceptance plan and procedure for point-to-point acceptance, and version. For comparisons, identify candidate paths, hypotheses, and metrics.>

## 2. Test Scope and Plan

- **Scope and exclusions** — <Requirements, scenarios, and boundaries in scope, with reasons for exclusions>
- **Test arrangement** — <Applicable work order or user acceptance guide, method, planned cases, order or dependencies. State the executor's basis and coverage for routine preparations, and the impact of missing information that cannot be derived.>
- **Completion criteria** — <Link the confirmed criteria. Changes to the criteria require confirmation outside the report.>
- **Integration scope confirmation** — <Source for the agreed scope, target version, environment, and main paths. Cite the launch request when it already confirms them.>

## 3. Test Environment

- **Version under test** — <Actual Git commit, relevant uncommitted changes, and artifact version>
- **Environment and entry point** — <Deployment environment, access or launch entry point, key configuration, dependencies, and versions>
- **Real and simulated components** — <Real services, substitute dependencies, simulated results, and limits on the conclusions>

## 4. Test Setup and Data

- **Setup** — <Account roles, permissions, dependency readiness, and actual setup results. Omit credentials.>
- **Data** — <Dataset or fixtures and version, source or construction method, initial state, and edge cases covered. Link the basis for routine data and boundary values, and cite the confirmation source for material decisions.>
- **Data recovery** — <Isolation, cleanup, and recovery method and actual outcome, or why this does not apply>
- **Setup gaps** — <Unmet conditions and affected cases, or None>

## 5. Execution and Coverage Summary

- **Planned and actual execution** — <Actual scope, time, and reasons for deviations>
- **Case counts** — <Total in scope and counts for Pass, Fail, Not run, and Blocked. Count each case once per batch. The four counts sum to the total. Record retries separately as evidence.>
- **Requirements coverage** — <Map each in-scope feature to its cases, scenarios, and ACs. Describe partial coverage, combinations of behaviors, and unverified items. When resuming or testing a changed version or environment, record what changed, why any earlier evidence still applies, and which cases were rerun.>

## 6. Test Details

List every case in scope. For each Not run or Blocked case, give the reason, impact, and condition for resuming. Use stable case IDs and link scenarios or ACs. Engineering verification may link a Task. Reuse the original case for a retest and link the previous batch. Record versions separately when they differ. Explain why reused evidence applies to the current version.

| Case / Requirement basis | Preconditions / Data | Method and actual steps | Expected outcome and criteria | Actual outcome and differences | Verdict | Evidence / Actual version | Issue reference |
|---|---|---|---|---|---|---|---|
| <ID and basis> | <Conditions> | <Steps or reproducible entry point> | <Confirmed criteria> | <Observed facts, or reason the case did not run> | <Pass / Fail / Not run / Blocked> | <Process and outcome evidence> | <Independent Issue link or None> |

Keep evidence of key intermediate steps for behaviors such as retry, cancellation, recovery, and concurrency. For applicable quality metrics, cite the confirmed conditions, statistical definition, and threshold and record the measured result. Link failed attempts involving the test setup or harness to the correction and rerun. Record execution results and human feedback separately.

For a Bug, link diagnosis checks, local fix checks, and post-fix retests to their actual versions and the original Issue. For diagnosis, record the candidate cause, predicted observation and evidence that would rule it out, actual observation, and conclusion. For a targeted retest or a local or integration check used as closure evidence, identify the original case or explain equivalence. Record the actual fixed version, environment, original outcome after the fix, required regressions and side effects, and any unmet Issue criteria. If execution requires real components or user feedback, state the remaining conditions and their effect on closure. Record Issue verification and the integration Test Gate against their respective scopes. Cite the version, environment, and coverage when reusing evidence.

## 7. Related Issues and Impact

| Issue reference | Related cases in this batch | Issue summary and impact on this batch's conclusion |
|---|---|---|
| <Independent Issue link or None> | <Case IDs> | <Observed issue and impact in this batch> |

Keep Issue references and their impact here. Use the [Issue template](issue_template.md) for the assignee, fix references, current status, and handling history. A defect finding requires evidence beyond a case being Not run, Blocked, or lacking evidence.

## 8. Test Conclusion and Limitations

- **Overall conclusion** — <Whether this batch met its completion criteria, the basis, and where the conclusion applies>
- **Remaining risks and unverified items** — <Related cases, Issues, and impact on acceptance>
- **Human confirmation** — <Experience requiring user action or judgment, feedback source and time, or pending verification and its effect on the Gate. State when this does not apply.>
- **Gate** — <For full integration regression, state the Test Gate, declared scope, actual version and environment, and supporting evidence. PASS requires every applicable feature and criterion in scope to be satisfied with the required evidence. Otherwise identify the gaps and resumption conditions. For other verification types, identify the applicable conclusion or mark this field not applicable.>

Preserve the facts for this batch, including failures fixed later. Record a retest as a new batch, which may use a separate section in the same file. If correcting a recording error, explain the reason and evidence. The Issue holds its status and closure basis, with links to the relevant batches. Integration reports reference the original ID and actual evidence. Include both in the task receipt. Update the Issue status only within the task's authorization, using the original criteria and observed results. Link the report and Issues from Status or Plan.
