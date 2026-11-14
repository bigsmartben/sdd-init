# Spec — {CAPABILITY} (Current Requirements)

> Use this template for detailed capability requirements. Use the applicable product-wide use cases, supported clients, experience principles, and acceptance scenarios from the project index when available. A scoped work order may use its own confirmed criteria and other accessible authoritative sources.

Use the location specified in [Repository Governance](../references/sdd-repository-governance.md#document-and-artifact-locations). Update the existing authoritative Spec identified in the project index.

## 1. References and Scope

- **Product use cases and key acceptance scenarios** — <Link applicable Blueprint PUCs and PACs, or cite the confirmed work order, Spec, or contract that defines this scope and criteria.>
- **Capability scope and exclusions** — <Detail the scope of this capability within the product scope>
- **Applicable environments** — <Link the product environments and add only capability-specific conditions>

## 2. Current Requirements

- FR-001: <Confirmed, observable behavior and applicable conditions. Preserve existing IDs.>

Record the requirements contract. Keep specific technical solutions, design patterns, internal classes, methods, and algorithms in their owning design or implementation artifacts. Detail the applicable use cases and acceptance dimensions from the sources above. Use the applicable AC for detailed conditions, thresholds, and pass criteria.

## 3. Detailed Acceptance Criteria

| ID | Given (precondition) | When (trigger) | Then (outcome and pass criteria) | Requirement / Product scenario | Evidence type |
|---|---|---|---|---|---|
| AC-001 | <Condition> | <Action> | <Behavior and applicable quality criteria, or a link to their authoritative source> | <FR / applicable scenario or work order reference> | <Required evidence> |

Define user-facing acceptance from the user or caller entry point. For user-observable quality metrics, the applicable AC records or links the confirmed measurement conditions, statistical definition, and threshold.

Cover applicable edge cases, failures, concurrency, cancellation, and recovery. Follow the [Testing Scope Constraints](../references/sdd-repository-governance.md#testing-scope-constraints). Record actual results, evidence, and verification gaps in the Test Report and link it from Status or Plan. AC, ARC, and Gate outcomes require their own evidence.

## 4. Requirements Prototype (Optional)

Use when the [Prototype Scope](../references/prototype.md#prototype-scope) applies. Otherwise omit this section.

- **Prototype and fixed version** — <HTML entry point, source, and corresponding version>
- **Applicable scenarios and ACs** — <How interactions and business states map to requirements>
- **Confirmation** — <Confirmed scope and items awaiting confirmation>

A confirmed medium-fidelity HTML prototype forms part of the requirements for actions, layout, and observable states. Keep business rules, permissions, and quality criteria in the Spec. Simulated data and mock interfaces require confirmation before becoming business requirements. Return conflicts between the Spec and prototype for confirmation.

## 5. Architecture References and Open Questions

- **Related Interface Contracts, Scenario Sequences, and ARCs** — <Links to authoritative clauses>
- **Open questions** — <Only material questions affecting the requirement. Omit if there are none.>

Preserve the identifiers and meaning of existing requirements, ACs, and historical evidence. Retain detailed requirements when reorganizing the product view.
