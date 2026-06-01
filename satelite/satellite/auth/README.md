# SaaS Multi-Tenant Authentication & Authorization

This module regulates security gates, JWT credentials, role permissions (RBAC), and subscription quotas.

---

## 1. Role-Based Access Control (RBAC)

Every user profile is tied to a specific organization. System access permissions are filtered by three distinct tiers:
1. **admin**: Full administrative permissions. Can add/remove member accounts, edit API keys, and manage billing.
2. **member**: Standard engineering account. Can trigger dynamic simulations, configure EKF twins, run optimizations, and download PDFs.
3. **viewer**: Read-only access. Restricted from invoking solving runs or training surrogates.

---

## 2. Quota Management & Redis Cache

Organization limits are regulated monthly in Redis and reset on monthly calendars:
* **Free Tier**: 100 simulations/month limit.
* **Pro Tier**: 1,000 simulations/month limit.
* **Enterprise Tier**: Unlimited simulation invocations.

If Redis goes offline, the quota tracking degrades gracefully to in-memory dictionaries.

---

## 3. JWT & API Key Headers

Authentication supports:
* **JWT Header**: `Authorization: Bearer <token>`
* **API Key Header**: `X-API-Key: <key>`
* **API Key Query**: `?api_key=<key>` (Backwards-compatible support for external telemetry clients).
