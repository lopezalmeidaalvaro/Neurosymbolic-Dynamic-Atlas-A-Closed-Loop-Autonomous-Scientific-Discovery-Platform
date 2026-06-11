# Known Technical Limitations & Constraints — AST-OS

This document explicitly logs the known limitations, mocked routes, and uncalibrated models in AST-OS. These limits represent standard developmental engineering steps rather than failures, and are documented for transparent scientific audit.

---

## 1. Physical Model Limitations

### A. Uncalibrated lumped historical models (`T48`)
- **Limitation**: The historical comparison models (`flight_heritage_compare.py`) utilize a single small cubesat capacity ($200 \text{ J/K}$) across ISS and Sentinel-2 spacecraft.
- **Consequence**: Transient integrations yield unphysical steady-state peak temperatures (Sentinel-2 peaking at **204°C** instead of stabilizing near **28°C**), resulting in a **176.3°C error**.
- **Mitigation needed**: capacities must be scaled based on structural wet masses: $C_i = M_i \cdot C_p$.

### B. EKF Covariance Saturation
- **Limitation**: Large telemetry sensor noise ($\sigma > 5.0^\circ\text{C}$) drives the error covariance matrix $P_k$ to grow exponentially during prediction phases.
- **Consequence**: State estimates diverge from actual physical trajectories, triggering false safe-mode shutdowns.
- **Mitigation needed**: Implement rigid covariance bound constraints.

---

## 2. API & Integration Mocks

### A. NOAA Space Weather Ingestion
- **Limitation**: The system architecture claims real-time NOAA solar activity ingestion to adjust space albedo fluxes. In reality, **there is zero active NOAA API integration code**.
- **Consequence**: Space solar reflections are modeled using standardized static LEO constants.

### B. Stripe SaaS Webhook Gateway
- **Limitation**: FastAPI webhook routes are designed for protocol trace audits.
- **Consequence**: Cryptographic webhook signature validation is bypassed by default on local test environments.

### C. SatNOGS Telemetry APIs
- **Limitation**: Live web requests to the SatNOGS server are caught and redirected immediately to local synthetic packet generators.
- **Consequence**: Telemetry processed in qualification testbeds is synthetically emulated.
