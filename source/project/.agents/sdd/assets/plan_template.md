# Plan — <Implementation goal>

> This template defines the implementation output. Follow the [implementation rules](../references/implementation.md) to prepare, adjust, and execute the Plan. Use the Task list as the Plan, maintaining one copy in the current Task record or the existing planning document.

A simple change may require one Task. Keep the required sections and fields, write only facts relevant to this change, and link existing material precisely. Lead with completed results, key changes, verification outcomes, and remaining work, then link the detailed Task list. Before execution, summarize the goal, change scope, and completion criteria. The full template is optional when presenting work for execution or confirmation.

## 1. Goal and Basis

- **Goal and scope** — <Intended change, affected scope, applicable constraints, and explicit exclusions>
- **Upstream work** — <Work order goal, scope, pass criteria, and links to the upstream acceptance plan and procedure. Reference the confirmed requirement, AC, Interface Contract, architecture decision, original Bug Issue, or original Review check as applicable.>
- **Current implementation** — <Code facts and entry points directly related to the change>

## 2. Task List

<!-- Repeat this block for each Task, including Plans with one Task. -->

### T001: <Goal with independently verifiable completion>

- **Basis** — <Relevant scenario or AC, Issue, Review check, or exploration goal. Link applicable interface and data constraints by clause. Keep Issue status and history in the Issue.>
- **Change scope** — <Actual file paths or explicit module boundaries. Mark new files.>
- **Implementation** — <Current approach and relevant trade-offs. Before execution, record enough to start. Identify any assumption that affects the approach or execution order and how to check it before relying on it. Update the approach as evidence changes.>
- **Dependencies** — <None, or direct prerequisite Task IDs and the condition each must meet. References must resolve within the list and form an acyclic graph.>
- **Completion criteria and local verification** — <Observable result required to complete this Task, targeted checks, expected outcomes, and limits. Map the checks to the upstream criteria they cover.>
- **Status** — <Pending / In progress / Failed / Blocked / Complete. Failed means an attempted action or check was unsuccessful. Blocked means a prerequisite or decision prevents progress. Keep the failure evidence if work later becomes blocked or resumes.>
- **Results and evidence** — <Not run, or the version or working-tree details, check outcomes, evidence links, and upstream criteria covered or still awaiting verification. A simple Task may use a Test Report in the current Task record.>

For a Bug Task, link the original Issue and the diagnosis evidence that supports the reported cause. Use the Implementation field for the chosen approach. If new evidence contradicts the diagnosis or a retest exposes an unresolved failure caused by this change, preserve the prior results and report the affected work and evidence under the same Issue ID in the existing Plan. In Results and evidence, record the fix version, link the evidence for the original or an equivalent scenario and any required regression checks, and identify the criteria still awaiting verification.

### Delivery Batches (when independently verifiable)

Use the Task's own verification for a single Task. For work that can be delivered in separately verifiable batches, use the table below.

| User goal or scenario / AC | Priority, if agreed | Task IDs | Observable result | Local verification |
| --- | --- | --- | --- | --- |
| <Reference the goal or scenario> | <Agreed priority or delivery order, if any> | <Tasks needed for this result> | <What this batch delivers> | <Targeted unit tests or other applicable local checks, with their prerequisites> |

### Execution DAG (multiple Tasks)

For a Plan with multiple Tasks, show the execution order as a compact DAG derived from the Dependencies fields. Identify shared prerequisites and the Task IDs that can run in parallel once their prerequisites and any shared-state conditions are met. Update the view when dependencies change.

## 3. Delivery Checks

- **Goal coverage and completion** — <Link completed and unfinished Tasks. Compare the actual changes and verification coverage with the upstream goal, applicable constraints, and current Plan.>
- **Blockers and next actions** — <Specific problem, affected Tasks, and resumption conditions, or None>
- **Coverage gaps and applicable follow-up** — <Work order criteria still awaiting verification and their executors. Link the upstream acceptance plan and procedure for applicable requirements acceptance, defect retest, architecture recheck, and refactoring behavior-preservation acceptance. Provide the entry points, known setup, and available evidence.>
