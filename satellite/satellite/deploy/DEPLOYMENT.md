# Deployment Guide: Autonomous Spacecraft Thermal OS Production Platform

This document describes how to build, deploy, and manage the production platform container network for the **Autonomous Spacecraft Thermal OS**. 

---

## 1. System Architecture

The deployment platform is decoupled into 5 microservices coordinated on a secure private bridge network (`thermal-net`):

```
       [ Client Browser ]
               │
      ( Port 80 / HTTP )
               ▼
       ┌───────────────┐
       │ Nginx Proxy   │
       └───────┬───────┘
               ├───────────────/ (Nextjs:3000)──────────────┐
               ├─────────/v1 or /api (FastAPI:8000)─────────┼──────────────┐
               └──────────/ws (WebSocket upgrade)───────────┼────────┐     │
                                                            ▼        ▼     ▼
                                                       ┌─────────┐ ┌───────────┐
                                                       │ Redis   │ │ FastAPI   │
                                                       │ Pub/Sub │ │ Backend   │
                                                       └─────────┘ └────┬──────┘
                                                                        ▼
                                                                  ┌───────────┐
                                                                  │ Timescale │
                                                                  │ Postgres  │
                                                                  └───────────┘
```

1. **Nginx Reverse Proxy (`thermal_nginx`)**: Listens on port 80. Routes traffic dynamically:
   * `/ws`: WebSocket upgrade to support real-time telemetry streams.
   * `/v1` or `/api`: FastAPI server.
   * `/`: Next.js frontend application.
2. **Next.js Frontend Client (`thermal_dashboard`)**: Compiled static server running on Node.js port 3000.
3. **FastAPI Backend Server (`thermal_api`)**: Uvicorn server running Python 3.11 on port 8000. 
4. **TimescaleDB Database (`thermal_postgres`)**: Persistent Timeseries SQL database with hypertable automatic time partitioning.
5. **Redis Broker Cache (`thermal_redis`)**: Asynchronous cache for role-based rate limits and Pub/Sub routing for Websockets.

---

## 2. Environment Setup

Copy `.env.example` to `.env` in this directory:
```bash
cp .env.example .env
```

Ensure the database passwords, JWT secret tokens, and encryption salts are configured securely:
* **SECRET_KEY**: Generated using a secure generator (e.g., `openssl rand -hex 32`).
* **API_KEY_SALT**: Salt to protect API key indices in the database.

---

## 3. Production Deployment Commands

All container workflows are managed via the included `Makefile`:

### Build and Launch the Stack
```bash
make up
```
This builds the FastAPI and Next.js Dockerfiles and boots all 5 containers in daemon background modes.

### Follow System Logs
```bash
make logs
```

### Check Service Statuses
```bash
make status
```

### Stop the Containers
```bash
make down
```

### Cold System Reset (WARNING: Clears database volumes!)
```bash
make reset
```

---

## 4. Reverse Proxy Optimizations

The reverse proxy configuration in `nginx.conf` has been specifically tuned for high-frequency spacecraft telemetry feeds:
* **Gzip Compression**: Compresses all JSON telemetry payloads dynamically to minimize payload bandwidth across high-latency orbits.
* **WebSocket Keep-Alives**: The `/ws` route overrides default connection limits (`proxy_read_timeout 86400s`), allowing connection sockets to remain open during extended mission sessions.
