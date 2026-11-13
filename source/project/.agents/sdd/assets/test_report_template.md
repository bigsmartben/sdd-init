# Test Report — <Subject and batch>

sdd-documenter completes this report from the confirmed goals, scope, and criteria, the executor's preparations based on them, and actual evidence. State the verification type: requirements acceptance, integration verification, local verification by the implementer, feasibility verification, Bug diagnosis, or retest. Use the [Architecture Review Record template](review_template.md) for architecture conformance.

Use the location specified in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). Follow the existing project index. For a simple Task, use this structure in the current Task record. Preserve historical paths and versions.

Include all eight sections. For a simple Task, record only the facts needed for this run and use precise references to existing material. Explain why a section or field does not apply, or identify missing information and its impact. Existing plans, guides, and cases can supply details when their applicability and any deviations are clear. Adjust links for the report's actual location.

## 1. Test Goals and Basis

- **Batch, verification type, executor, and time** — <Actual details>
- **Subject and goal** — <Capability, module, or candidate approach and what this run aims to establish>
- **Basis** — <Spec scenarios or ACs, confirmed engineering goals, Quickstart or verification approach, and version. For comparisons, identify candidate paths, hypotheses, and metrics.>

## 2. Test Scope and Plan

- **Scope and exclusions** — <Requirements, scenarios, and boundaries in scope, with reasons for exclusions>
- **Test arrangement** — <Confirmed Plan or guide, method, planned cases, order or dependencies. State the executor's basis and coverage for routine preparations, and the impact of missing information that cannot be derived.>
- **Completion criteria** — <Link the confirmed criteria. Changes to the criteria require confirmation outside the report.>

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
- **Requirements coverage** — <Map cases to scenarios and ACs. Describe partial verification, combinations of behaviors, and unverified items separately. Assess coverage from this mapping.>

## 6. Test Details

List every case in scope, including cases that were Not run or Blocked, with reasons. Use stable case IDs and link scenarios or ACs. Engineering verification may link a Task. Reuse the original case for a retest and link the previous batch. Record versions separately when they differ. Explain why reused evidence applies to the current version.

| Case / Requirement basis | Preconditions / Data | Method and actual steps | Expected outcome and criteria | Actual outcome and differences | Verdict | Evidence / Actual version | Issue reference |
|---|---|---|---|---|---|---|---|
| <ID and basis> | <Conditions> | <Steps or reproducible entry point> | <Confirmed criteria> | <Observed facts, or reason the case did not run> | <Pass / Fail / Not run / Blocked> | <Process and outcome evidence> | <Independent Issue link or None> |

Keep evidence of key intermediate steps for behaviors such as retry, cancellation, recovery, and concurrency. Record automated results and human feedback separately.

For a Bug, link diagnosis checks, local fix checks, and post-fix retests to their actual versions and the original Issue. For diagnosis, record the candidate cause, predicted observation and evidence that would rule it out, actual observation, and conclusion. For a local or integration check used as closure evidence, identify the original case or explain equivalence, record actual execution and required regression results on the fixed version, and identify any unmet Issue criteria. Record Issue verification and the integration Test Gate against their respective scopes. Cite the version, environment, and coverage when reusing evidence.

## 7. Related Issues and Impact

| Issue reference | Related cases in this batch | Issue summary and impact on this batch's conclusion |
|---|---|---|
| <Independent Issue link or None> | <Case IDs> | <Observed issue and impact in this batch> |

Keep Issue references and their impact here. Use the [Issue template](issue_template.md) for the assignee, fix references, current status, and handling history. A defect finding requires evidence beyond a case being Not run, Blocked, or lacking evidence.

## 8. Test Conclusion and Limitations

- **Overall conclusion** — <Whether this batch met its completion criteria, the basis, and where the conclusion applies>
- **Remaining risks and unverified items** — <Related cases, Issues, and impact on acceptance>
- **Human confirmation** — <Item, feedback source, and time. State when confirmation is unnecessary or still pending. Record it separately from automated results.>
- **Gate** — <Link the actual verdict, scope, and version from the relevant workflow. PASS requires that workflow to run.>

Preserve the facts for this batch, including failures fixed later. Record a retest as a new batch, which may use a separate section in the same file. If correcting a recording error, explain the reason and evidence. Update Issue status in the Issue with links to discovery and applicable local or integration evidence. Link the report and Issues from Status or Plan.
