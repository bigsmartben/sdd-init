# Plan — <Implementation goal>

> Follow the [execution modes and Plan tiers](../references/implementation.md#plan-分档). Maintain one Plan in the current Task record or the existing planning document. Select the smallest tier that proves the work: Light, Standard or Long-running. Do not copy unused sections from a larger tier into a simple task.

## Light Plan

Use for one local change with no meaningful cross-Task dependency. A small Task may remain in the current work record.

- **Goal, scope and exclusions** — <Intended result and what is out of scope>
- **Work order, mode and write boundary** — <Original ID, `investigate` / `prepare` / `implement` / `fix` / `refactor`, authorization endpoint and allowed writes>
- **Completion criteria and local check** — <Observable pass criteria, check entry point and environment>
- **T001 / Status** — <One independently verifiable Task; Pending / In progress / Failed / Blocked / Complete>
- **Results, version and gaps** — <Changes, checks and outcomes, actual version or working-tree fingerprint, coverage, pending Gate, impact, owner and resumption condition>

## Standard Plan

Use for multiple files, dependencies, or separately verifiable results.

### 1. Goal and Basis

- **Goal and scope** — <Intended change, affected scope, applicable constraints, and explicit exclusions>
- **Readiness** — <Original work order ID, execution mode, pass criteria, authorization endpoint, write boundary and completion conditions. Link applicable Spec / AC, Issue attribution, Review CHK, acceptance entry and environment. If a required field is missing, report `needs-input`, `blocked` or `partial` instead of implementing.>
- **Current implementation** — <Code facts and entry points directly related to the change>

### 2. Task List

<!-- Repeat this block for each Task, including Plans with one Task. -->

### T001: <Goal with independently verifiable completion>

- **Basis** — <Relevant scenario or AC, Issue, Review check, or exploration goal. Link applicable interface and data constraints by clause. Keep Issue status and history in the Issue.>
- **Change scope** — <Actual file paths or explicit module boundaries. Mark new files.>
- **Implementation** — <Current approach and relevant trade-offs. Before execution, record enough to start. Identify any assumption that affects the approach or execution order and how to check it before relying on it. Update the approach as evidence changes.>
- **Dependencies** — <None, or direct prerequisite Task IDs and the condition each must meet. References must resolve within the list and form an acyclic graph.>
- **Completion criteria and local verification** — <Observable result required to complete this Task, targeted checks, expected outcomes, and limits. Map the checks to the upstream criteria they cover.>
- **Status** — <Pending / In progress / Failed / Blocked / Complete. Failed means an attempted action or check was unsuccessful. Blocked means a prerequisite or decision prevents progress. Keep the failure evidence if work later becomes blocked or resumes.>
- **Results and evidence** — <Not run, or actual changes, version and working-tree fingerprint, commands and results, evidence links, covered criteria, and pending or failed items. Preserve earlier failures after a successful rerun.>

For a Bug Task, link the original Issue and the diagnosis evidence that supports the reported cause. Use the Implementation field for the chosen approach. If new evidence contradicts the diagnosis or a retest exposes an unresolved failure caused by this change, preserve the prior results and report the affected work and evidence under the same Issue ID in the existing Plan. In Results and evidence, record the fix version, link the evidence for the original or an equivalent scenario and any required regression checks, and identify the criteria still awaiting verification.

#### Delivery Batches (when independently verifiable)

Use the Task's own verification for a single Task. For work that can be delivered in separately verifiable batches, use the table below.

| User goal or scenario / AC | Priority, if agreed | Task IDs | Observable result | Local verification |
| --- | --- | --- | --- | --- |
| <Reference the goal or scenario> | <Agreed priority or delivery order, if any> | <Tasks needed for this result> | <What this batch delivers> | <Targeted unit tests or other applicable local checks, with their prerequisites> |

#### Execution DAG

Show the execution order derived from Dependencies. Tasks that modify the same file or shared mutable state are serial. Parallel Tasks must be free of file and state conflicts. For asynchronous work, show the explicit completion condition and handoff evidence that unlocks the dependent Task; waiting does not mean the dependency passed.

### 3. Delivery Checks

- **Goal coverage and completion** — <Link completed and unfinished Tasks. Compare the actual changes and verification coverage with the upstream goal, applicable constraints, and current Plan.>
- **Blockers and next actions** — <Specific problem, affected Tasks, and resumption conditions, or None>
- **Coverage gaps and applicable follow-up** — <Work order criteria still awaiting verification and their executors. Link the upstream acceptance plan and procedure for applicable requirements acceptance, defect retest, architecture recheck, and refactoring behavior-preservation acceptance. Provide the entry points, known setup, and available evidence.>

## Long-running Extension

Add this to a Standard Plan only when work must survive a pause or multiple rounds.

| Recovery point | Effective mode and authorization / confirmations | Completed Tasks and valid evidence | Next ready action | Invalidating changes or conditions |
| --- | --- | --- | --- | --- |
| <Version / time / checkpoint> | <What is still authorized and confirmed> | <Actual results that still apply> | <Task or required input> | <Version, environment, worktree, criterion or design changes that require reassessment> |

Record gaps with their affected Tasks, owner and resumption condition. Do not duplicate Status, Issue or Test Report fields when a precise reference is sufficient.
