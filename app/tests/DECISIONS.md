# DECISIONS.md

## What I Built and What I Skipped

I implemented the core subscription lifecycle. I created subscription, got subscription, canceled subsctription and billing webhook processing.
I focused on the most important business functionality and the areas most likely to fail in production.
I did not implement the optional endpoint. Instead, I designed the data model so that billing events can be stored and exposed later through a dedicated history endpoint.
This allowed me to prioritize correctness and business logic over completeness.

---

## Ambiguities I Found in the Spec

### Grace Period Duration

The specification mentions a grace period but does not define its duration.
I chose a 7-day grace period because it is a common approach in subscription systems and keeps the implementation simple.

### Payment Events for Cancelled Subscriptions

The specification does not define what should happen if a payment event arrives after a subscription has already been cancelled.
I decided that `cancelled` is a terminal state. Payment events are still recorded for audit purposes but do not reactivate the subscription.

### Payment Events During Trial

The specification states that subscriptions begin with a 7-day trial and later receive billing events.
I assumed that billing events received before the end of the trial should be ignored because the subscription is not yet billable.

---

## Data and Storage Choices

### Storage

I chose SQLite because:
- It requires no external infrastructure.
- It is easy to run locally.
- It is sufficient for the scope of this assignment.

For a production system I would use PostgreSQL together with migrations.

### Subscription Entity

Fields: id, user_id, status, created_at.

### BillingEvent Entity

Fields: event_id, subscription_id, event_type, amount, timestamp.
The BillingEvent table also supports future audit history requirements because every billing-related event can be stored and queried.

---

## Trade-offs I Made

I chose simplicity over completeness.
Examples:
- SQLite instead of PostgreSQL
- Simple synchronous processing instead of background workers
- Minimal validation instead of a full business rules engine

Given the time constraints, I preferred implementing a small but reliable slice rather than a larger incomplete solution.

---

## The Scenario

Scenario:
- 14:00:01 payment succeeds at the carrier.
- 14:00:02 the user presses Cancel.
- The cancel request reaches the API before the webhook arrives.

### Final State

**cancelled**

### Reasoning

The user explicitly requested cancellation and the system successfully processed that request.
When the delayed payment webhook arrives, the payment event is recorded for audit purposes but does not reactivate the subscription.

### Example Audit History

1. Carrier processes successful payment.
2. User cancels subscription.
3. Delayed webhook arrives.
4. Webhook is stored but ignored because the subscription is already cancelled.

This preserves both billing history and user intent.

---

## Edge Cases and Failure Modes

### Duplicate Webhook Delivery

Handled in code.

The carrier guarantees at-least-once delivery, so duplicate events may arrive.

Events are deduplicated using the unique `event_id`.

### Unknown Subscription

The API returns an error if a billing event references a subscription that does not exist.

### Multiple Cancel Requests

Cancelling an already cancelled subscription does not change its state.

### Invalid Event Types

Only the following event types are accepted:

- payment.succeeded
- payment.failed

### Concurrent Requests

Not fully handled.

A production system would require stronger transaction handling and concurrency controls.

---

## What I Would Do Differently 

- Implement the history endpoint.
- Add more automated tests.
- Add tests for duplicate webhook processing.
- Add tests for race conditions.
- Introduce database migrations.
- Add structured logging.
- Implement automatic grace-period expiration.
- Improve validation and error handling.

---

## How I Used AI on This Assignment

I used ChatGPT to:
- Brainstorm the overall project structure.
- Review state transition logic.
- Generate an initial FastAPI scaffold.
- Identify potential edge cases.
- Review webhook deduplication logic.

I manually reviewed all generated code before using it.
One example where AI output was not suitable was around subscription cancellation. Some generated solutions reactivated cancelled subscriptions after receiving a successful payment webhook. I rejected that approach because it conflicted with my decision that cancelled should be a terminal state.