# Code Review Rules

Use the confirmed design and applicable [architecture guidance](../references/architecture-rules.md#在目标仓库中落实). Give each rule a stable project identifier, link the governing clause, and identify the project responsibilities and entry points a reviewer can check. Reuse the existing identifier for an equivalent constraint. Project choices about responsibility allocation, runtime behavior, failure policy, and isolation require a confirmed basis; recommendations alone are not violation criteria.

## CRR-001 · <Fact or responsibility>

- **Design basis** — <Specific Blueprint or Interface Contract link and clause identifier>
- **Checklist mapping** — <Applicable stable AR checklist IDs and their source version; retain valid project-specific constraints without a shared counterpart.>
- **Project constraint** — <Modules, authoritative entry points, and allowed interactions>
- **Applicability and check timing** — <Applicable objects and conditions, direct changes or indirect effects that trigger a check, and local, CI, or review execution timing>
- **Evidence path** — <Call entry point and read, write, recovery, or failure paths to inspect>
- **Check method** — <Dependency inspection, semantic review, contract test, or failure experiment, with an executable entry point or concrete inspection procedure>
- **Pass criteria** — <Observable outcomes and confirmed budgets or thresholds under the applicable conditions>
- **Violation criteria** — <Observable implementation or behavior that violates the design>

Reference existing code, configuration, tests, and review mechanisms; a rule does not require a new module or document. Link applicable project objects through the separate [Review Matrix](review-matrix_template.md). Keep batch tasks and execution evidence in the applicable review or test report. Missing or unexecuted evidence is not a pass.

## Open Questions

<Record specific questions where design evidence is missing or conflicting. Link the relevant clauses and add the rule after confirmation.>
