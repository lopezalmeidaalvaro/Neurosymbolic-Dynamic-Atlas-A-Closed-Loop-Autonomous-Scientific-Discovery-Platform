# Spacecraft Thermal OS (AST-OS) - SaaS Authentication & Security Design

This document describes the design of JWT sessions, header API keys, middleware validations, and RBAC (Role-Based Access Control) policies protecting AST-OS SaaS endpoints.

---

## 1. Dual-Path Authentication Design

AST-OS provides two secure auth paths to accommodate both browser-based users and headless automated operations:

### A. Headless Automated Operations (API Keys)
Automated flight telemetry pipelines or remote OpenMDAO nodes authenticate using persistent keys passed via Headers:
`X-API-Key: pro_enterprise_key_xyz987`
* **Storage**: Generated as high-entropy `key_...` UUID tokens at registration and stored in the SQLite `users` table.
* **Scope**: Allows fast integration with scripts, CI/CD, and flight bus command pipes.

### B. Interactive Dashboard Operations (JWT Tokens)
Browser-based users or Next.js dashboards authenticate using temporary JSON Web Tokens (JWT) signed with a secure, high-entropy server secret:
`Authorization: Bearer <JWT>`
* **Structure**: Signed utilizing standard HMAC-SHA256 signatures, containing claims:
  ```json
  {
    "username": "satellite_operator",
    "email": "operator@spaceframe.org",
    "tier": "pro",
    "exp": 177984000
  }
  ```

---

## 2. Middleware Validation Sequences

The dependency injector `verify_access` acts as the security middleware gate:

```text
Incoming API Call
       │
       ├───> Has "Authorization: Bearer <JWT>" Header?
       │            ├───> YES: Decodes JWT, Verifies signature & expiration.
       │            └───> NO:
       │                 │
       │                 └───> Has "X-API-Key" Header or Query Parameter?
       │                              ├───> YES: Looks up key in SQLite database.
       │                              └───> NO: Returns HTTP 403 Forbidden.
       │
       └───> Query Usage Table: Counts requests in last 24 hours.
                    ├───> Within Limits (e.g. < 10,000 for Pro): Logs Request, Returns 200 OK.
                    └───> Limit Exceeded: Returns HTTP 429 Too Many Requests.
```

---

## 3. Persistent Quotas & Multi-Tenant Tiers

* **Storage Schema**: The SQLite `usage` table archives query timestamp logs linked to user keys.
* **Sliding Window Validation**: Requests are aggregated within a 24-hour sliding window:
  `SELECT COUNT(*) FROM usage WHERE api_key = ? AND timestamp > ?`
* **Zero Heap Overheads**: Multi-tenant quotas are resolved dynamically at database level, keeping the active FastAPI server footprint extremely lightweight.
