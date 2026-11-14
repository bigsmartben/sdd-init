# Prompt Review Record — <Subject and batch>

Use the current task record or the project location in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). Record the findings and their evidence. When revisions are authorized, keep the comparison and each retest in the same record.

## Scope and baseline

- **Request and authorized endpoint** — <Goal, review only or revise, writable files, and permissions for isolated runs and external effects>
- **Inputs and versions** — <Target, baseline and candidate versions as applicable, confirmed authorities, actual entry and load path, scope and precedence>
- **Baseline observations** — <Original deviations and evidence gaps, separately from confirmed expectations>

## Rules, scenarios, and findings

| Rule | Authority and load location | Condition | Owner | Action or prohibition | Authorization | Exception | Completion criterion | Before and after mapping |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <Rule ID> | <Source clause and effective entry> | <Trigger> | <Responsible party> | <Expected decision or action> | <Required authority> | <Applicable exception> | <Observable evidence> | <Locations and semantic effect> |

For each critical scenario, show the task DAG or list nodes with their direct prerequisites. Identify observable reads, decisions, actions, handoffs, output and evidence, including branch conditions, forbidden paths and separate retry attempts. Link nodes to relevant rules.

| Finding | Location and scenario | Evidence and consequence | Impact | Recommendation or actual change |
| --- | --- | --- | --- | --- |
| <ID and affected rule or node> | <Version, location, trigger> | <Expected and observed difference> | <Affected behavior or decision> | <Proposed or authorized revision> |

## Verification and receipt

- **Run conditions** — <Input, permissions, tools, model configuration, initial state, version and run IDs; comparison method and repetitions when relevant>

| Scenario and criterion | Static comparison | Observed runtime results and side effects by version | Evidence or gap |
| --- | --- | --- | --- |
| <Scenario, rule or node IDs and expected behavior> | <Coverage and finding> | <Actual reads, decisions, actions or refusals, output and state; mark unrun scenarios> | <Trace, artifact, failure or missing input> |

- **Stage result** — <Findings, revisions, covered behavior, stability evidence where applicable, unverified scope, and recovery conditions. Report runtime success only for observed results that satisfy the agreed criteria.>
- **Open decisions and resumption conditions** — <Evidence, impact, and decision, authorization or trigger needed to continue>
