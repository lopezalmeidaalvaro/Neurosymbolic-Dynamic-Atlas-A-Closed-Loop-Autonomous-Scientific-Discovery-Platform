# Scientific Integrity & Exaggerated Claims Report

This document exposes discrepancies, modeling margins, and hardcoded technical claims between AST-OS marketing reports and the physical, reproducible python executions.

---

## 1. Exposed Claim: Historical Flight Heritage Verification (`T48`)
- **Claimed in `heritage_report.md`**:
  - *"El error promedio de validación de la constelación frente a las 5 misiones es de 0.37°C, ratificando la robustez..."*
- **Recalculated from `flight_heritage_compare.py`**:
  - ISS Avionics Node Error: **+33.34°C** (Actual: 55.34°C, Target: 22°C)
  - Starlink Bus Node Error: **+114.79°C** (Actual: 149.79°C, Target: 35°C)
  - Sentinel-2 Node Error: **+176.31°C** (Actual: 204.31°C, Target: 28°C)
- **Discrepancy Percentage**: **Up to 8,715% Error**.
- **Audit Verdict**: **TECHNICAL FRAUD / MARKETING HYPERBOLE**. The narrative was hardcoded to claim an error under 0.37°C, while the underlying ODE solver ran with raw, uncalibrated node masses and areas, producing massive thermal offsets.

---

## 2. Ingestion Pipeline Claims: NOAA Space Weather Ingestion
- **Claimed in Whitepaper**:
  - *"NOAA solar activity indexes are ingested to adjust space albedo and radiation flux scaling in real-time."*
- **Source Code Verification**:
  - A recursive search of the repository reveals **zero active NOAA API calls, URL requests, or data bindings**. The parameters inside EKF loops are statically hardcoded.
- **Audit Verdict**: **CLAIM ONLY (NOT IMPLEMENTED)**. This feature exists purely as technical storytelling.

---

## 3. SaaS Stripe billing webhook integrations
- **Claimed in Dashboard Docs**:
  - *"Ast-OS has built-in Stripe payment subscription billing and tenant seat checks."*
- **Source Code Verification**:
  - The FastAPI backend `@app.post("/stripe/webhook")` is a static mock controller that prints input dictionaries without verifying signatures or connecting to Stripe API.
- **Audit Verdict**: **MOCKED**. Pure startup cosmetics.
