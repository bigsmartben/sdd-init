# Quickstart — <Capability>

Use the location specified in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). This structure captures reproducible steps and expected outcomes for the capability or the current acceptance scope. Use a Test Report for actual run results.

## 1. Verification Goal and Scope

- **Spec** — <Link the adjacent spec.md and applicable scenarios or ACs. Where applicable, link the fixed version of the confirmed HTML prototype, its scenarios and confirmed scope, and relevant Interface Contracts.>
- **Goal and scope** — <What the guide can establish and what it excludes. Return missing requirements or criteria for discussion.>

## 2. Setup and Launch

- **Runnable version** — <Source and instructions for obtaining it>
- **Environment, permissions, dependencies, and data** — <Name the environment and the setup steps or commands. Provide example inputs and how to obtain or recreate the required starting state. For routine data, boundary values, and execution order, state what the executor derived from the Spec, ACs, or Task and what it covers. Preserve the agreed scope and criteria. Omit credentials.>
- **Launch command or access point** — <Runnable command or usable entry point>

For a user-facing work order, reuse the provided acceptance steps or prepare them from confirmed criteria. Record the known entry point and setup. For integration testing, fill in the runnable version and environment under the [Testing Scope Constraints](../references/sdd-repository-governance.md#testing-scope-constraints). Update the existing authoritative guide when authorized to maintain a formal project record.

## 3. Scenario Verification

Reuse the Spec scenario and AC identifiers and organize by user goal. Cover normal behavior, edge cases, failures, cancellation, recovery, and combinations within the applicable scope. Add data, metrics, and exception conditions for complex scenarios as needed. For user-observable quality metrics, specify where to measure from the user or caller entry point and link the confirmed measurement conditions, statistical definition, and threshold.

| Scenario / AC | Preconditions | Action or command | Expected outcome and observation | Required evidence |
| --- | --- | --- | --- | --- |
| <ID> | <Setup> | <Executable steps> | <Confirmed expectation and observable criteria> | <Evidence linked to scenario and version> |

Write the acceptance path from the user's entry point through the observable outcome. Give exact actions or runnable commands, the input to use, and where to observe the expected result. Expand a scenario into ordered steps when the table is insufficient. For retries, recovery, and other multistep behavior, pair the decisive actions with intermediate observations as well as the final outcome. Link the applicable Spec or Interface Contract for requirements and semantics.

## 4. Failures and Recovery

<Describe failure, cancellation, and retry where applicable. Explain how to restore the required starting state before rerunning scenarios that change data or environment state. Link existing rules and mark missing rules as awaiting confirmation.>

## 5. Results and Progress References

<Link the Test Report and relevant Status or Plan.> The Test Report records the actual Git commit, relevant uncommitted changes, environment, scenario outcomes (Pass, Fail, Not run, or Blocked), evidence, retests, and any required human confirmation. Record automated results and human confirmation separately in the report. Use this section to link the records.
