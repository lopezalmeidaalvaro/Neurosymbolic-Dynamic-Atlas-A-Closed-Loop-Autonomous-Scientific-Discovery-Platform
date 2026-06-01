# Spacecraft Thermal OS (AST-OS) - SaaS Cloud Deployment Targets

This document evaluates the top 4 production-grade cloud deployment targets for hosting the AST-OS SaaS FastAPI applications, comparing cost, resources, scaling ease, and configurations.

---

## 1. Cloud Provider Comparison Matrix

| Cloud Target | Estimated Cost (Monthly) | Allocated CPU / RAM | Scaling & Orchestration | Primary Use Case / Target Audience |
| --- | :---: | :---: | :---: | --- |
| **Hetzner Cloud (VPS)** | **$5.90 - $12.50 USD** | 2 vCPU / 4 GB RAM | Manual (Docker Compose / Systemd) | **Recommended (Best Cost/Performance)**. Excellent for self-managed deep-tech hosting. |
| **Railway.app** | $10.00 - $30.00 USD | 1 vCPU / 2 GB RAM | Automated Git-push trigger scaling | Fast developer prototyping and automatic TLS certifications. |
| **Fly.io** | $15.00 - $45.00 USD | 1 vCPU / 2 GB RAM | Global edge nodes deployments | Geographically distributed API targets close to SatNOGS ground telemetry antennas. |
| **Render.com** | $7.00 - $25.00 USD | 1 vCPU / 1 GB RAM | Automated Dockerfile git hooks | Simple single-service deployment with basic persistent disks. |

---

## 2. Infrastructure Setup & Specifications

### Hetzner Cloud (VPS) Setup Spec
* **Target OS**: Ubuntu 22.04 LTS.
* **Volume Mounts**: 40 GB NVMe persistent disk for TimescaleDB and SQLite.
* **Virtual Private Network**: Private VPC connecting the FastAPI container to PostgreSQL to block external DB intrusion.

### Fly.io Edge Setup Spec
* **Virtualization**: Firecracker microVMs.
* **Database Bindings**: Utilizes Fly Postgres clusters with multi-region read replicas.
