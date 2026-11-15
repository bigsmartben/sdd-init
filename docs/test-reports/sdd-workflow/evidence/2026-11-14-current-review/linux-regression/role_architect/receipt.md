`sdd-architect` receipt: completed.

- Updated [Blueprint](docs/blueprint.md:9) and [Scenario Sequence](docs/create-sequence.md:5) with atomic order/outbox persistence, asynchronous dispatch, event-ID retries, and rollback behavior.
- Preserved the contract: `201` may precede delivery; persistence failure returns `503` without a created event.
- Documentation checks: **0 errors, 0 warnings**. `git diff --check` passed.
- Only the two authorized design documents changed. No implementation changes. Mermaid rendering was not tested.