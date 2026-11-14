# Scenario Sequence

## Create order

- SCN-001 For a valid POST /orders, the API authenticates the caller, validates input and calls the Order Service. The Order Service writes order state and one OrderCreated outbox record through the repository in a single storage transaction. Successful commit makes both durable and eligible for dispatcher access. The API can then return 201 with the order identifier independently of asynchronous event delivery. Transaction failure rolls back both writes and leads to 503 without a success response or created event. The dispatcher reads committed records, publishes asynchronously to consumers and retries by event ID.

Applicable responsibilities and invariant: ARC-001 and ARC-002 in the [Blueprint](blueprint.md). Public response and event semantics: CON-001 in the [create contract](create-contract.md). Design basis: the [confirmed decision](decision.md).

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service as Order Service
    participant Repository
    participant Dispatcher
    participant Consumers
    Client->>API: POST /orders
    Note over API: Authenticate caller and validate input
    API->>Service: Create order
    Service->>Repository: Write order and one OrderCreated outbox record atomically
    Note over Repository,Dispatcher: No visibility to dispatcher before successful commit
    alt Transaction commits successfully
        Note over Repository: Order and outbox record are durable
        par Return durable order identifier
            Repository-->>Service: Commit succeeded, order identifier
            Service-->>API: Durable order identifier
            API-->>Client: 201 with order identifier
        and Dispatch committed event asynchronously
            Dispatcher->>Repository: Read committed outbox records
            Repository-->>Dispatcher: OrderCreated with event ID
            Dispatcher-)Consumers: Publish OrderCreated
            opt Publication requires retry
                Dispatcher-)Consumers: Retry OrderCreated by event ID
            end
        end
    else Transaction fails
        Note over Repository: Roll back both writes; no created event becomes dispatchable
        Repository-->>Service: Persistence failure
        Service-->>API: Persistence failure
        API-->>Client: 503 without a success response
    end
```

The parallel branches impose no ordering between the 201 response and event delivery. Dispatch may remain pending after the response, and consumers use events asynchronously. The retry path retains the event ID.
