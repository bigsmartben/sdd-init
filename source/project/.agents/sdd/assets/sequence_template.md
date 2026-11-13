# Scenario Sequence

> Show key interactions among modules, public interfaces, and external actors. Keep internal classes, private methods, and algorithm steps outside this view. Use the project index to find the authoritative location. A module can share a Scenario Sequence with other modules.

## Key Scenarios

| Scenario | Requirement basis | Modules and external actors | Interface Contract |
|---|---|---|---|
| <Scenario name and anchor> | <PUC / PAC / AC> | <Confirmed participants> | <Public interface and relevant ARC links> |

Select scenarios that clarify interactions, ordering, or races. Link the existing BDD scenarios and draw diagrams for the interactions that need them. Link Blueprint PUCs and PACs for product goals and acceptance dimensions, Spec ACs for detailed expectations, conditions, and quality criteria, and the owning Interface Contract for public payloads and result semantics.

## <Scenario name>

- **Scenario and step IDs** — <Reuse existing identifiers for Review references. Record actual results in the Test Report.>
- **Related requirements** — <PUC / PAC / AC links>
- **Preconditions** — <Applicable environment, state, and eligibility. Link existing agreements.>
- **Participants** — <Modules or public interfaces and relevant external actors>

<Insert a UML sequence diagram or a Mermaid sequenceDiagram with equivalent interaction semantics. Use participants and messages from the confirmed design. Confirm new interfaces through the project design process.>

Show the relevant details:

- Initiator, call direction, requests, responses, and asynchronous notifications. Distinguish sending from receipt and acceptance from completion.
- Required ordering, parallelism and joins, and races such as completion before cancellation or cancellation before completion.
- Applicable rejection, failure, timeout, late response, unknown outcome, and recovery paths.
- Identity and version correlation, the authoritative state commit point, when eligibility expires, and required acknowledgments.

Distinguish asynchronous messages from synchronous calls. Show a successful return only when the outcome is known. Draw interactions in sequence only where ordering is guaranteed and show synchronous waiting only where the design requires it.

### Additional Conditions

<Add conditions the diagram cannot show and link the relevant Interface Contract. After failure, evaluate the Task outcome, domain side effects, resource eligibility, and action permissions separately under the applicable agreements. Describe rollback or replay only when the agreement provides for it.>

### Open Questions

<Link the relevant Task or Review conclusion. Identify unresolved responsibilities or interfaces explicitly. Omit this section if there are no open questions.>

## Scope of the Sequence

Use the Blueprint deployment view for deployment locations, its component view for responsibilities and dependencies, and the Interface Contract for data and result semantics. Use activity diagrams for complex branches, joins, or processing that the sequence does not already convey. Distinguish control flow from object flow. Add state or ER diagrams to the relevant Interface Contract when needed. Internal class diagrams are optional.

See the [Observability Architecture Rules](../references/observability-baseline.md) for applicable constraints and the [Architecture Review Record](review_template.md) for rule mappings. Keep execution evidence in the Test Report and link it from Status or Plan. Applying the template leaves existing sequences in place and Gate decisions follow the applicable verification process.
