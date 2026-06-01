# Spacecraft Thermal Digital Twin Deployment Manual

This document provides administrative instructions to compile, containerize, secure, and deploy the **Production Spacecraft Thermodynamic Digital Twin** API microservices to cloud environments (AWS/GCP) or private virtual private servers (VPS).

---

## 📟 1. Cloud Architecture Overview

The production deployment features a double-layer proxy architecture separating high-speed public entry and background solver computations:

```
                  ┌──────────────────────────────────────────────┐
                  │                 HTTPS Client                 │
                  └──────────────────────┬───────────────────────┘
                                         │ Port 443 (SSL via Let's Encrypt)
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │              Nginx Reverse Proxy             │ (SSL termination, access logging,
                  │               (Docker Container)             │  and Nginx 10 req/s rate-limiting)
                  └──────────────────────┬───────────────────────┘
                                         │ Port 8000 (Local bridge network)
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │               FastAPI API Server             │ (JWT key auth check, SQLite rate-limiter,
                  │               (Docker Container)             │  Matplotlib/ReportLab PDF reporting)
                  └──────────────────────────────────────────────┘
```

---

## 📦 2. VPS Deployment via Docker Compose

For standard Ubuntu VPS nodes, use Docker Compose to spawn the service stack:

### Prerequisites:
Install Docker Engine and Docker Compose:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
```

### Steps to Deploy:
1. Navigate to the cloud folder:
   ```bash
   cd satellite/cloud
   ```
2. Build and launch all services in background detached mode:
   ```bash
   docker-compose up -d --build
   ```
3. Verify that Nginx and the API container are running:
   ```bash
   docker-compose ps
   ```

---

## 🚀 3. Automated Cloud Push (AWS/GCP Orchestrator)

For automatic deployments targeting AWS Elastic Container Registry (ECR) + EC2, or Google Container Registry (GCR) + Cloud Run, execute our production script:

```bash
python satellite/cloud/deploy_production.py
```

### Script Execution Sequence:
* **Docker Packaging:** Empackets all solvers, physical boundaries, and models into `lopezalmeidaalvaro/thermal-twin:v0.3.0`.
* **ECR Registry Authentication:** Queries AWS CLI credentials and authenticates Docker CLI.
* **Image Registry Push:** Pushes the tag to the designated AWS/GCP cloud registries.
* **Instance Provisioning:** Fires AWS EC2 `t3.medium` instances or GCP Cloud Run nodes.
* **SSL Certificate Configuration:** Queries Let's Encrypt CA to verify DNS boundaries and download certificates.

---

## 🛡️ 4. API Security & Rate Limiting

The FastAPI endpoint implements:
* **API Key Auth:** Requires header `X-API-Key`. Unauthenticated queries receive `403 Forbidden`.
* **SQLite Rate-Limiter:**
  * **Plan "free":** Bounded at **100 req/min**.
  * **Plan "pro":** Bounded at **1,000 req/min**.
  * Excess requests receive `429 Too Many Requests`.
* **Daily Rotating Logging:** Logs are parsed in structured JSON format and saved with daily rotation inside `satellite/logs/thermal_api.log`.
