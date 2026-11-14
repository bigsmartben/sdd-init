# Scenario Sequence

## Key Scenarios

| Scenario | Requirement basis | Modules and external actors | Interface Contract |
|---|---|---|---|
| [SCN-001 — Create order](#create-order) | [Confirmed decision](decision.md), [ARC-002](blueprint.md#architecture-invariants) | Client, API, Order Service, repository, dispatcher, consumers | [CON-001](create-contract.md) |

## Create order

- **Scenario ID** — SCN-001.
- **Related requirements** — [CON-001](create-contract.md) and [ARC-002](blueprint.md#architecture-invariants), confirmed in the [design decision](decision.md).
- **Preconditions** — A caller submits an authenticated, valid `POST /orders`; the diagram covers persistence and dispatch after authentication and validation.
- **Participants** — Client, API, Order Service, repository, dispatcher and event consumers; responsibilities are defined in the [Blueprint](blueprint.md#responsibilities).

```mermaid
sequenceDiagram
    actor Client
    participant API
    participant Service as Order Service
    participant Repository
    participant Dispatcher
    participant Consumers
    Client->>API: POST /orders
    Note over API: Authenticate caller and validate input
    API->>Service: Create order
    Service->>Repository: Persist order and one OrderCreated outbox record atomically
    Note over Repository,Dispatcher: No uncommitted writes are visible to the dispatcher
    alt Transaction commits successfully
        Note over Repository: Commit both writes durably
        par API response after durability
            Repository-->>Service: Both writes committed durably
            Service-->>API: Order identifier; durable creation
            API-->>Client: 201 with order identifier
        and Independent asynchronous dispatch after commit
            Dispatcher->>Repository: Read committed outbox records
            Repository-->>Dispatcher: OrderCreated record with event ID
            loop Publish attempt; retry on failure using the same event ID
                Dispatcher-)Consumers: Publish OrderCreated asynchronously
            end
        end
    else Transaction fails
        Note over Repository: Roll back both order and outbox writes
        Repository-->>Service: Persistence failure
        Service-->>API: Creation failed
        API-->>Client: 503
        Note over Dispatcher,Consumers: No committed record for this creation; no created event
    end
```

### Additional Conditions

The storage commit is the authoritative durability point. The dispatcher cannot publish this creation from an uncommitted transaction. A transaction failure rolls back both writes; the API returns 503 without an order success response or created event.

The response and dispatch branches have no required ordering relative to each other after commit. The API may return 201 while dispatch is pending and does not wait for publication, delivery or retries. Retries retain the event ID of the committed outbox record; this sequence does not assert exactly-once delivery. Public response and event semantics remain owned by [CON-001](create-contract.md).
