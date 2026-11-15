# Orders Blueprint

## Responsibilities

- ARC-001 The API authenticates clients, the Order Service owns order state, and the repository commits changes on behalf of the service. The API remains the public response boundary. See the [create contract](create-contract.md) and the [create sequence](create-sequence.md).

## Architecture Invariants

- ARC-002 The Order Service writes order state and exactly one OrderCreated outbox record through the repository in the same storage transaction. Neither write is visible to the dispatcher unless the transaction commits successfully. Transaction failure rolls back both writes; the API returns 503 without a success response or created event. The dispatcher reads committed outbox records, publishes asynchronously, and retries by event ID. After the transaction is durable, the API may return 201 with the order identifier while dispatch remains pending; event delivery is not a prerequisite for that response. Basis: the [confirmed design decision](decision.md) and CON-001 in the [create contract](create-contract.md). See SCN-001 in the [create sequence](create-sequence.md#create-order) for ordering and failure paths.
