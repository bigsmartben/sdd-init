# Blueprint — Product and Architecture

> Record confirmed objectives. Refer to Status or Tasks for implementation progress and to Test Reports for verification results and evidence. Maintain one Blueprint for the entire product. It defines high-level use cases, key experiences, and acceptance dimensions. Refer to the relevant Spec for detailed FRs and ACs and to the owning Interface Contract for mechanisms. Keep each detail in its authoritative document.

Link the product requirement that drives a decision beside the corresponding responsibility or invariant. Link the relevant Scenario Sequence when ordering, concurrency, or failure affects the user experience.

## 1. Product Goals and Scope

Describe the target users, their problem, the value, and what is included, optional, or excluded. Capture key experiences in the use cases and BDD scenarios below. Keep essential details and link the relevant PUCs and PACs.

## 2. Clients and Operating Conditions

| Environment ID | Client and usage context | Required operating conditions | Capability differences and support scope |
|---|---|---|---|
| PENV-01 | <Device and browser or app> | <Confirmed network, permission, and version requirements> | <Product commitments and limitations> |

Describe client support commitments separately from deployment locations. Record version coverage in acceptance evidence and collect open questions in section 8.

## 3. Product Use Cases

Organize product-wide use cases by user goal. Use a Mermaid `flowchart` to show actors, the system boundary, goals, and relevant relationships. Use a `subgraph` for the system boundary, with use cases inside and actors outside. Connect related elements. Use `include`, `extend`, or generalization only when the relationship matches its UML semantics.

| Use case ID | Actor, goal, and key experience | Applicable environment and detailed requirements |
|---|---|---|
| PUC-01 | <Confirmed user goal> | <PENV or relevant Spec section> |

## 4. High-Level Acceptance Scenarios and Dimensions

Use Given–When–Then to describe representative scenarios and acceptance dimensions. A table or Gherkin is sufficient. An automation framework is optional.

| ID / Use case | Given | When | Then — High-level expectation and acceptance dimension |
|---|---|---|---|
| PAC-01 / PUC-01 | <Specific precondition> | <Specific trigger> | <High-level expectation and acceptance dimension. Link the Spec AC for the detailed criteria.> |

Cover key experiences, success, edge cases, failure, cancellation, and recovery according to risk. Describe operations separately when their preconditions, triggers, or rules differ. Parameterize only when the expected behavior follows the same logic. Give distinct triggers, cancellations, and failures their own expected outcomes. Describe an actual scenario for each entry and use links to support it. When splitting a scenario, preserve traceability to the original PAC and retain existing FR and AC identifiers.

Use PACs for product quality dimensions. Refer to Spec ACs for specific conditions, thresholds, timing boundaries, units, statistical definitions, and evidence types. Link available acceptance evidence for the actual integrated version and agreed environment. Follow the [Testing Scope Constraints](../references/sdd-repository-governance.md#testing-scope-constraints).

## 5. System Structure and Component Responsibilities

Follow the containment hierarchy: **System > Subsystem > Component > Module**. A system defines the overall boundary; a subsystem groups related capabilities within it; a component owns a cohesive responsibility within a subsystem; a module is an internal implementation unit of a component. Components are the smallest architectural granularity in the Blueprint. Keep module decomposition and internal implementation details in linked engineering documents, not in Blueprint diagrams or responsibility tables.

Use a hierarchical component diagram to show the system boundary, subsystem boundaries, and their components, with responsibilities, I/O, interfaces, allowed and prohibited dependencies, key concepts, and their relationships. Distinguish containment from interaction and dependency relationships. Record who produces and consumes each concept and who owns authoritative data. Define essential terms briefly. Add a separate relationship diagram only if it conveys information absent from the component diagram and overall sequence.

| System / Subsystem | Component | Responsibilities, state ownership, and prohibited interactions | Interface Contract |
|---|---|---|---|
| <Owning system / subsystem> | <Confirmed component> | <Requester, decision maker, writer, side-effect executor, authoritative state owner, and evidence of completion> | <Owning Interface Contract section> |

Add a compact data table when useful to explain sources, authority, permitted reads and writes, and lifecycle. Preserve these distinctions when combining tables. Put detailed payloads, authorization, cancellation, results, and failure semantics in the owning Interface Contract.

## 6. Deployment and Runtime Mapping

Map the logical components defined in section 5 to confirmed deployment units and runtime environments. Use their existing names or identifiers in both views. These are complementary views of the same architecture, not successive levels of the containment hierarchy: a subsystem is not necessarily a service, and a component is not necessarily a process. Multiple components may share a process, and a component may have multiple runtime instances. Do not require a one-to-one mapping.

Use a deployment view to show hosting, instance topology, runtime isolation, and communication across boundaries. A Mermaid flowchart can express this view without UML deployment syntax. Identify separate processes only when the confirmed deployment design calls for them. Link existing engineering documentation for source directories and build entry points.

| Logical component reference | Deployment unit / Runtime location | Instances and isolation | Cross-boundary Interface Contract |
|---|---|---|---|
| <Component from section 5, qualified by subsystem> | <Confirmed unit and hosting environment> | <Instance topology and process or other isolation boundary> | <Interface defined in section 5 and its owning contract, or not applicable> |

Account for every in-scope component's runtime placement. Identify external systems and non-runtime assets explicitly rather than forcing them into process deployments; record unresolved placement in section 8. Deployment changes must preserve logical responsibilities and authoritative state ownership. Trace runtime communication to the logical interfaces; sharing a process does not permit bypassing dependency restrictions. Describe how interfaces cross runtime boundaries here, while keeping detailed protocols and failure semantics in the owning Interface Contract.

Record confirmed design strategies, rationale, costs, and applicable conditions. Link the relevant PUCs and PACs, and refer to the Spec for product quality criteria. Use runtime constraints to check whether the logical design is feasible; reconcile conflicts across both views rather than silently changing responsibilities in the deployment view.

## 7. Architecture Invariants

| ID | Constraint | Basis |
|---|---|---|
| <Stable ARC identifier> | <Rule that holds during normal operation, failure, concurrency, cancellation, and recovery> | <Responsibility or Interface Contract reference> |

Record project invariants the user has confirmed. Preserve stable identifiers, applicability conditions, and the strength of each constraint. Refer to section 5 for existing responsibility lists and section 6 for deployment and runtime constraints. List unconfirmed environments, frameworks, and strategies as open questions. Use the confirmed design and this template as the basis. Reading the architecture rules and adding rule mappings are outside this step.

### Architecture Review Assets

After sdd-refactor initializes the project review assets, keep a fixed link here to the effective project architecture rules and the independent Review Matrix. Retain the project's established paths; the default matrix location is `docs/review-matrix.md`. Do not copy matrix rows or batch conclusions into the Blueprint. Before initialization, state that the assets have not been initialized rather than creating a link to a missing file. For changes to an initialized project's subsystems, modules, components or their relationships, follow the [review asset maintenance contract](../references/sdd-repository-governance.md#目标仓库的-code-review-rules); sdd-refactor maintains the matrix through Main.

## 8. Key Interactions and Open Questions

| Product scenario | Interface Contract / Scenario Sequence |
|---|---|
| <PUC or PAC and interaction goal> | <Links to public interfaces and key interactions> |

Use the index to link responsibilities and detailed flows. Use the [Scenario Sequence template](sequence_template.md) to describe normal ordering, parallelism, races, cancellation, late results, unknown outcomes, and recovery across public interfaces. Keep internal algorithms outside this view. Record interface and failure semantics in the [Interface Contract](contract_template.md). Use activity diagrams for complex branches, joins, or data processing, distinguishing control flow from object flow. Include state or ER diagrams when useful without decomposing components into internal implementation units. Keep internal class diagrams in linked engineering documents.

| Open question | Source, impact, and decision needed |
|---|---|
| <Material gap> | <Related clause or Task> |

Collect open questions here and link any authoritative list already maintained in a Task. Keep uncertain or infeasible items open. Fill sections as applicable. Record governance activity and check evidence in the Task.

## Architecture Modeling and Assessment

Sections 1–4 cover product goals and acceptance dimensions. Section 5 defines the logical system structure, subsystems, and component responsibilities. Section 6 maps those components to deployment and runtime boundaries, with trade-offs. Section 7 records invariants across both views. Section 8 indexes key interactions and open questions. Combine sections or link existing documents to suit the project while preserving the component-level granularity limit and explicit logical-to-runtime mapping. The project confirms subsystem and component boundaries, architectural planes, technical patterns, and deployment. Link engineering documents for module decomposition and directory layout. Record missing decisions as open questions.

Follow the [Repository Governance](../references/sdd-repository-governance.md#authoritative-documents) for document ownership and the [Document Writing Rules](../references/document-writing.md) when consolidating clauses or verifying a migration.
