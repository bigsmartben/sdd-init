# Quickstart — <Product or acceptance scope>

Use the location specified in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). This user acceptance guide covers every confirmed feature in the product scope under acceptance for full functional integration regression. Use a Test Report for actual run results and link the guide used for that run.

## 1. Verification Goal and Scope

- **Spec** — <Link the confirmed product use cases, applicable Specs, scenarios and ACs, and relevant Interface Contracts. Where applicable, link the fixed version of the confirmed HTML prototype and its confirmed scope.>
- **Goal and scope** — <State the agreed product scope, its boundaries, and the main user paths. Identify any criterion or prerequisite that needs to be resolved.>

## 2. Setup and Launch

- **Runnable version** — <Target revision or artifact, where to obtain it, and how to verify the version actually running>
- **Environment, permissions, dependencies, and data** — <Name the environment and the setup steps or commands. Provide example inputs and how to obtain or recreate the required starting state. For routine data, boundary values, and execution order, state what the executor derived from the Spec, ACs, or Task and what it covers. Preserve the agreed scope and criteria. Omit credentials.>
- **Launch command or access point** — <Runnable command or usable entry point>

Derive the coverage list and runnable steps from confirmed criteria, reusing applicable work-order steps or existing guides. Fill in the runnable version and environment under the [Testing Scope Constraints](../references/sdd-repository-governance.md#testing-scope-constraints). Update the existing authoritative guide when the task calls for a formal project record.

## 3. Scenario Verification

Map every confirmed feature in scope to its scenario or AC and the steps below. Reuse the Spec scenario and AC identifiers and organize by user goal. Cover normal behavior, failures, edge cases, recovery, combinations, and interactions across modules within the applicable scope. Add data, metrics, and exception conditions for complex scenarios as needed. For user-observable quality metrics, specify where to measure from the user or caller entry point and link the confirmed measurement conditions, statistical definition, and threshold.

| Feature / Scenario / AC | Preconditions | Action or command | Expected outcome and observation | Required evidence |
| --- | --- | --- | --- | --- |
| <Feature and stable IDs> | <Setup and starting data> | <Executable steps> | <Confirmed expectation and observable criteria> | <Evidence linked to scenario and version; identify any required human action or judgment> |

Write the acceptance path from the user's entry point through the observable outcome. Give exact actions or runnable commands, the input to use, and where to observe the expected result. Expand a scenario into ordered steps when the table is insufficient. For retries, recovery, and other multistep behavior, pair the decisive actions with intermediate observations as well as the final outcome. Link the applicable Spec or Interface Contract for requirements and semantics.

## 4. Failures and Recovery

<Describe failure, cancellation, and retry where applicable. Explain how to restore the required starting state before rerunning scenarios that change data or environment state. Link existing rules and mark missing rules as awaiting confirmation.>

## 5. Results and Progress References

<Link the Test Report and relevant Status or Plan.> The Test Report records the actual Git commit, relevant uncommitted changes, environment, scenario outcomes (Pass, Fail, Not run, or Blocked), evidence, retests, and any required human confirmation. Record automated results and human confirmation separately in the report. Use this section to link the records.
