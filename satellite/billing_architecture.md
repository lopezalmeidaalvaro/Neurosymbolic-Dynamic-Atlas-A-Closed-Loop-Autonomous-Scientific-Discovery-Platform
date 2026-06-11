# Spacecraft Thermal OS (AST-OS) - SaaS Billing & stripe Integration Architecture

This document details the multi-tenant subscription tiers, payment integration flows, and webhook routing mechanics linking Stripe to the AST-OS SQLite database store.

---

## 1. Product Tiers Plan Design

We offer three subscription tiers to satisfy various aerospace operations requirements:

| Plan Tier | Price (Monthly) | Daily Quota | Features Included |
| --- | :---: | :---: | --- |
| **Developer (Free)** | $0.00 USD | 100 requests | Lumped simulators, API key validation, basic Swagger. |
| **Professional (Pro)**| $149.00 USD | 10,000 requests | Coupled 6-node LEO solver, JWT session auth, ReportLab PDF reports. |
| **Mission (Enterprise)**| $899.00 USD | Custom (100k+) | Swarm constellation scheduling, 24/7 dedicated support, custom EKF noise calibrations. |

---

## 2. Payments Checkout Flow

```mermaid
sequenceDiagram
    participant Client as Spacecraft Dashboard
    participant API as AST-OS FastAPI Server
    participant DB as SQLite / Timescale Database
    participant Stripe as Stripe Gateway

    Client->>API: POST /v1/stripe/checkout (email, plan)
    API->>DB: Save session state (Pending)
    API->>Stripe: create Checkout Session
    Stripe-->>API: Return Checkout URL & Session ID
    API-->>Client: Redirect to Checkout URL
    Client->>Stripe: Perform Payment
    Stripe->>API: POST /v1/stripe/webhook (checkout.session.completed)
    API->>DB: Upgrade User Tier to "pro" in Users Table
    API-->>Stripe: 200 OK
```

---

## 3. Webhook Controller Processing Rules

The webhook endpoint `POST /v1/stripe/webhook` processes Stripe payloads dynamically:
1. **Event Interception**: Captures incoming POST requests. In production, Nginx forwards the payload and signatures.
2. **Signature Validation**: Validates the webhook signature using `STRIPE_WEBHOOK_SECRET` to prevent headers spoofing.
3. **Database Integration**:
   * Inspects `event.type`.
   * For `checkout.session.completed` or `charge.succeeded`, extracts `billing_details.email`.
   * Triggers the SQLite update query:
     `UPDATE users SET tier = 'pro' WHERE email = ?`
4. **Graceful Degrades**: If a payment fails or cancels, the customer portal downgrades the tier to `free` instantly to block high-frequency simulations quota access.
