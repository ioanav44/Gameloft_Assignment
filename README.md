
# Take-Home Assignment — Subscription Service API

## Read this first

This assignment has two parts: code, and a written document called `DECISIONS.md` where you explain the choices you made.

**The written part is more important than the code.** A small, working slice of the API with a thoughtful `DECISIONS.md` is a much stronger submission than a complete API with a thin one. If you only have time for one, prioritise `DECISIONS.md`.

## How long should this take?

Most candidates spend **4–7 hours** of focused work. If you are going much longer, you are probably building too much — stop, take stock, and write `DECISIONS.md`.

## The spec is bigger than the time you have

This is on purpose. You will not be able to build everything described below.

Pick the slice you think is most important. Build that slice well. Use `DECISIONS.md` to explain what you chose to build, what you skipped, and why.

## Context

You are building a small slice of a subscription billing system. This is the kind of system that powers digital content stores: users sign up for a monthly subscription, get charged by their mobile carrier (the mobile network operator that adds the charge to the user's phone bill), and can cancel or be suspended if a payment fails.

## What you are building

An HTTP API that manages the lifecycle of a subscription.

### Endpoints

**Required:**

1. `POST /subscriptions` — Create a new subscription for a user. New subscriptions start with a 7-day free trial.
2. `GET /subscriptions/{id}` — Return the current state of a subscription.
3. `POST /subscriptions/{id}/cancel` — Cancel a subscription.
4. `POST /webhooks/billing` — Receive billing events from a carrier (see below).

**Optional:**

5. `GET /subscriptions/{id}/history` — Return the audit history of a subscription. If you do not implement this, describe in `DECISIONS.md` how you would store and expose audit history.

### Subscription states

A subscription has at least these states: `trialing`, `active`, `grace`, `cancelled`.

The basic transitions are:

- A new subscription starts in `trialing` for 7 days.
- After the trial, the carrier sends a `payment.succeeded` event. The subscription becomes `active`. Future successful payments keep it `active`.
- A `payment.failed` event on an `active` subscription moves it to `grace`. From `grace`, a successful payment moves it back to `active`. If the grace period ends, the subscription becomes `cancelled`.
- A user-initiated cancel moves the subscription to `cancelled`.

Where the spec is silent, you decide.

### The billing webhook

Two event types from the carrier — `payment.succeeded` and `payment.failed`. Each event has:

- `event_id` (string, unique per event)
- `subscription_id`
- `timestamp` (when the event was created by the carrier)
- `amount`

**The carrier guarantees at-least-once delivery.** Any single event may be delivered to your webhook more than once, with the same `event_id`. Your system needs to handle this.

### Scenario you must answer

This is a real situation we have seen in production. Your `DECISIONS.md` must include your answer.

> A user's billing is scheduled for 14:00. At 14:00:01 the carrier processes the charge successfully and queues a `payment.succeeded` webhook. At 14:00:02 the user clicks "Cancel" in the app.
>
> Because of network conditions, the cancel request reaches your API and is processed *before* the webhook from the carrier arrives.
>
> What is the final state of the subscription? What does the audit history look like? Explain your reasoning.

There is no single correct answer — we want to see how you reason, not what state you pick. Be brief.

## Constraints

- **Language:** Python, Node.js, or PHP. Any framework, or none.
- **Storage:** Your choice. Postgres, SQLite, in-memory, JSON file — anything. Explain your choice.
- **Auth:** Out of scope. Assume requests are already authenticated. You can read a `tenant_id` from a header if useful.
- **Hosting:** None required. We must be able to run your code locally with one or two commands.

## Tests

Write a test suite covering the cases most likely to break this system in production.

## Deliverables

A Git repository (zip file or link) containing:

### 1. Source code

The API itself.

### 2. `README.md`

- How to install and run the code.
- How to run the tests.
- How to call each endpoint (curl examples are fine).

### 3. `DECISIONS.md` *(see "Read this first" — this is the most important part)*

It must include the following sections:

**What I built and what I skipped.** Which slice did you pick? What did you leave out? Why?

**Ambiguities I found in the spec.** List things that were unclear, what you decided, and why. There are several — finding them is part of the assignment.

**Data and storage choices.** Describe the shape of your data (fields, types, relationships), why this shape and not another, why your storage choice fits here, and what you would change for production. Note how your data shape supports the audit history requirement.

**Trade-offs I made.** Places where you picked option A over option B, and your reasoning.

**The scenario.** Your answer to the cancel-during-payment scenario above.

**Edge cases and failure modes.** List every edge case you thought about, whether or not you wrote a test for it. For each one, say: did you handle it in code? Test it? Knowingly leave it unhandled? Why?

A short list of edge cases you knowingly skipped is a better answer than a long list of tests for things that do not matter.

**What I would do differently with more time.** Be specific. "Add tests" tells us nothing. "Add a test that runs the same webhook twice — I am not sure my dedupe logic is correct" tells us a lot.

**How I used AI on this assignment.** Which tools, for what tasks, where it helped you most, and how you checked the output. We use AI heavily on the team — you are expected to use it. We are more interested in *how you work with AI* than in whether you used it.

Include at least one example where the AI output was wrong or did not fit the problem. Briefly say what you did about it.

For example: *"I used Claude to scaffold the FastAPI project. I wrote the state machine by hand because I wanted to be sure I understood it. I asked Claude to review my dedupe code and it pointed out that I was not handling concurrent requests — I noted this in `DECISIONS.md` but did not fix it."*

### What a good `DECISIONS.md` entry looks like

Example from a different problem (a URL shortener):

> **Ambiguity: what happens when two users shorten the same URL?**
>
> The spec did not say. I had two options: return the same short code to both users (deduplicate by URL), or generate a new short code each time.
>
> I chose to generate a new short code each time. My reasoning: if two users shorten the same URL, they probably want their own analytics on it later. Deduplication would mix their click counts together. The cost of generating new codes is small.
>
> A real production system might let the user choose. I did not build that because the spec did not ask for it.

Notice three things:

1. It names the ambiguity clearly.
2. It says what the choice was *between*, not just what was chosen.
3. It gives reasoning, including cost and trade-offs.

One short paragraph per ambiguity. No essays.

## What we are looking for

- Code that runs in one or two commands and that you can explain on a short call.
- A consistent state machine — no transitions that contradict each other.
- A `DECISIONS.md` that shows you noticed gaps in the spec and made deliberate choices.
- Tests focused on what is most likely to break.
- A scope choice that makes sense.

## Submission

Send us the repository link or zip. Include a one-paragraph note on how it went: what was clear, what was confusing, any questions you had, and anything you would push back on. Questions are welcome — we treat them as part of the signal.