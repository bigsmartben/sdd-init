# Review Matrix — <Project>

> Persistent project architecture coverage, maintained by sdd-refactor. The Blueprint links to this file. Keep batch tasks, findings, remediation and execution results in the Architecture Review Record.

## 1. Basis and Confirmation

- **Blueprint and contracts** — <Confirmed clauses and their versions; retain the project's existing paths.>
- **Project rules** — <Authoritative rules in the Blueprint or Code Review Rules, with their stable IDs and versions. Reference constraints rather than copying their authoritative text.>
- **Checklist basis** — <Applicable stable IDs and version of the shared architecture guidance.>
- **Asset confirmation** — <User-confirmed initial content or latest additions, changes and removals, their impact, and the confirmation reference. Pending proposals do not replace the effective matrix.>

## 2. Object Coverage

Enumerate the actual subsystems, modules, components and cross-object collaboration boundaries from the Blueprint. Retain existing identifiers. Use RM-001 onward for new entries; do not renumber retained entries or reuse a retired ID for a different constraint. Select meaningful object–rule relationships rather than expanding every possible combination.

| Matrix ID | Object, granularity and parent | Design basis | Project rule and checklist IDs | Applicability and rationale |
|---|---|---|---|---|
| RM-001 | <Subsystem / module / component or collaboration path; parent and participants> | <Blueprint / contract clauses> | <Project rule links; shared checklist IDs> | <Applicable with conditions / Not applicable with reason / Pending decision with gap and resumption conditions> |

Include required but unimplemented objects. Identify coverage of dependencies, state authority and failure propagation across object boundaries. A missing project decision remains pending; an implementation observation is not a design decision.

## 3. Applicable Checks

### RM-001: <Object and constraint>

- **Subject and paths** — <Responsibilities, interfaces, source/configuration locations and callers; cite the authoritative project rule.>
- **Applicability and timing** — <Conditions, direct changes or indirect effects that require this check.>
- **Check method and evidence path** — <Concrete semantic/dependency inspection, path tracing, contract test or runtime procedure, with relevant preconditions and observations.>
- **Pass and violation criteria** — <Observable outcomes and project-confirmed budgets or thresholds, or precise referenced criteria.>
- **Related entries** — <Cross-module relationships and constraints to check together, or None.>

Repeat for applicable entries. Record pending design decisions and their affected coverage here without treating them as implementation violations. Preserve effective conditions and exceptions when consolidating entries.

## 4. Use and Maintenance

For each review batch, select entries according to the requested goal and impact. Generate CHK review tasks in the [Architecture Review Record](review_template.md), bind the actual matrix/rule snapshot, and confirm that batch's scope and endpoint with the user. Existing explicit confirmation is reusable. This matrix contains no batch assignee, PASS/FAIL result or remediation progress.

When structure, responsibilities, dependencies, contracts or applicable rules change, sdd-refactor presents the affected additions, changes and removals for user confirmation before updating this file and its Blueprint link. Unchanged entries need no new asset confirmation. Historical review records retain their original matrix/rule snapshot and evidence; do not rewrite their conclusions to match this edition.
