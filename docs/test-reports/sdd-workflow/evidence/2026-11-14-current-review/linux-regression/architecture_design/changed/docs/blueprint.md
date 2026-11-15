# Orders Blueprint

## Responsibilities

- ARC-001 The API authenticates clients, the Order Service owns order state, and the repository commits changes on behalf of the service. The API remains the public response boundary. See the [create contract](create-contract.md) and the [create sequence](create-sequence.md).

The Order Service writes order state and one OrderCreated outbox record through the repository in the same storage transaction. The dispatcher reads only committed outbox records, publishes asynchronously, and retries by event ID. The dispatcher depends on committed storage state; the API response does not depend on dispatch completion. Order state remains authoritative in storage under the Order Service's ownership.

## Architecture invariants

- ARC-002 Order state and its OrderCreated outbox record commit atomically. Neither write is visible to the dispatcher before a successful commit. A transaction failure rolls back both writes and the API returns 503, with no success response or created event. Once the transaction is durable, the API may return 201 with the order identifier while dispatch remains pending; event delivery is not a prerequisite. The dispatcher publishes committed records asynchronously and retries by event ID. This preserves [CON-001](create-contract.md) and is realized in [SCN-001](create-sequence.md#create-order), based on the [confirmed design decision](decision.md).
