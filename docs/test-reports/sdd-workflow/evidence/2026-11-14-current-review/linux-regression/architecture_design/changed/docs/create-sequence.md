# Scenario Sequence

## Create order

- SCN-001 The API authenticates the caller, validates input and calls the Order Service. The Order Service persists the order and one OrderCreated outbox record in the same storage transaction through the repository. A successful commit makes the records visible to the dispatcher and permits the API to return 201 with the order identifier. The dispatcher publishes asynchronously and retries by event ID. A transaction failure rolls back both writes and returns 503 without a success response or created event.

Participants are the caller, API, Order Service, repository, transactional storage, dispatcher, and event consumers. This sequence follows [ARC-001 and ARC-002](blueprint.md) and preserves the public response and event semantics in [CON-001](create-contract.md).

```mermaid
sequenceDiagram
    actor Caller
    participant API
    participant Service as Order Service
    participant Repository
    participant Storage as Transactional storage
    participant Dispatcher
    participant Consumer as Event consumers

    Caller->>API: POST /orders
    Note over API: Authenticate caller and validate input
    API->>Service: Create order
    Service->>Repository: Persist order and one OrderCreated outbox record atomically
    Repository->>Storage: Write both records in one transaction
    Note over Storage,Dispatcher: Neither write is visible to dispatcher before commit
    alt Transaction commits successfully
        Note over Storage: Both records committed and durable
        par API response after durability
            Storage-->>Repository: Commit succeeded
            Repository-->>Service: Persistence succeeded, order identifier
            Service-->>API: Order identifier
            API-->>Caller: 201 with order identifier
        and Asynchronous dispatch after commit
            Dispatcher->>Storage: Read committed outbox records
            Storage-->>Dispatcher: OrderCreated record with event ID
            Dispatcher-)Consumer: Publish OrderCreated asynchronously
            Note over Dispatcher,Consumer: On publication failure, retry by the same event ID
        end
    else Transaction fails
        Storage-->>Repository: Failure; both writes rolled back
        Repository-->>Service: Persistence failed
        Service-->>API: Persistence failed
        API-->>Caller: 503
        Note over Storage,Consumer: No committed outbox record, no created event
    end
```

The two success branches require a successful commit but do not require an ordering between the 201 response and publication. Dispatch may remain pending when 201 is returned. Publication failure leaves the committed order and outbox record durable for dispatcher retries by event ID; it does not cause the transaction-failure response. The dispatcher never publishes records from a failed transaction. The diagram specifies the confirmed design, not evidence of runtime implementation.
