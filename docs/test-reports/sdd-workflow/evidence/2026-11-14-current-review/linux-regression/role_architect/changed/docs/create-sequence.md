# Scenario Sequence

## Create order

- SCN-001 For a valid POST /orders, the API authenticates the caller, validates input and calls the Order Service. The service writes order state and one OrderCreated outbox record through the repository in the same storage transaction. Successful commit makes both durable and makes the outbox record visible to the dispatcher. The API may then return 201 with the order identifier independently of asynchronous dispatch. Transaction failure rolls back both writes and the API returns 503 without a success response or created event. The dispatcher reads committed records, publishes asynchronously to consumers, and retries by event ID.

Design basis: ARC-001 in the [Blueprint responsibilities](blueprint.md#responsibilities), ARC-002 in the [Blueprint invariants](blueprint.md#architecture-invariants), and CON-001 in the [create contract](create-contract.md).

```mermaid
sequenceDiagram
    actor Client
    participant API
    participant Service as Order Service
    participant Repository
    participant Dispatcher
    participant Consumers

    Client->>API: POST /orders (valid request)
    API->>API: Authenticate caller and validate input
    API->>Service: Create order
    Service->>Repository: Write order and one OrderCreated outbox record in one transaction
    Note over Repository,Dispatcher: Uncommitted writes are not visible to the dispatcher
    alt Transaction commits successfully
        Note over Repository: Order and outbox record are durable together
        par Complete public response
            Repository-->>Service: Commit succeeded
            Service-->>API: Durable order identifier
            API-->>Client: 201 with order identifier
        and Dispatch committed event asynchronously
            Dispatcher->>Repository: Read committed outbox records
            Repository-->>Dispatcher: OrderCreated record with event ID
            Dispatcher-)Consumers: Publish OrderCreated asynchronously
            Note over Dispatcher,Consumers: Retry publication by event ID when needed
        end
    else Transaction fails
        Note over Repository: Roll back both writes
        Repository-->>Service: Persistence failure
        Service-->>API: Persistence failure
        API-->>Client: 503
        Note over Repository,Consumers: No committed outbox record for this attempt; no created event
    end
```

The response and dispatch branches have no required ordering relative to each other after commit. Consumers use events asynchronously, and dispatch may still be pending when the API returns 201, as required by CON-001.
