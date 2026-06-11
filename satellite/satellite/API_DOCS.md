# Spacecraft Thermal Twin Commercial API Technical Documentation

This document describes the secure, high-fidelity REST API endpoints exposed by the Cubesat Thermodynamic Digital Twin production platform.

---

## 🔒 1. Authentication & Security Policy

All production endpoints (with the exception of core health and authentication endpoints) require a valid **API Key** passed via one of two methods:
1. **Request Header:** `X-API-Key: <your_api_key>`
2. **Query Parameter:** `?api_key=<your_api_key>`

Unauthenticated queries receive `403 Forbidden`. If your rate-limit is exceeded, the server returns `429 Too Many Requests`.

---

## 📟 2. Rate Limiting Tiers

Requests are metered in sliding windows of 60 seconds:
- **Plan "free":** Bounded at **100 requests per minute**.
- **Plan "pro":** Bounded at **1,000 requests per minute**.

You can query your current request counts via `/v1/usage`.

---

## 🚀 3. API Version 1 Endpoint Reference

All new production endpoints are prefixed with `/v1/`. Legacy unversioned paths are retained for backward compatibility.

### 🔑 3.1 Register Account
Creates a new user profile and returns a secure, auto-generated API Key.
- **URL:** `/v1/auth/register` (or `/auth/register`)
- **Method:** `POST`
- **Body:**
```json
{
    "username": "spaceflight_operator",
    "email": "operator@agency.gov",
    "password": "secure_admin_password_123"
}
```
- **Response (200 OK):**
```json
{
    "status": "success",
    "message": "User registered successfully.",
    "api_key": "key_bc0f124d98a24cf1",
    "tier": "free",
    "rate_limit": "100 req/min"
}
```

---

### 🔑 3.2 Login Account
Retrieve the active API Key for an existing profile.
- **URL:** `/v1/auth/login` (or `/auth/login`)
- **Method:** `POST`
- **Body:**
```json
{
    "username": "spaceflight_operator",
    "password": "secure_admin_password_123"
}
```
- **Response (200 OK):**
```json
{
    "status": "success",
    "api_key": "key_bc0f124d98a24cf1",
    "tier": "free"
}
```

---

### 📈 3.3 Query API Usage Metering
Returns monthly usage statistics.
- **URL:** `/v1/usage` (or `/usage`)
- **Method:** `GET`
- **Headers:** `X-API-Key: <key>`
- **Response (200 OK):**
```json
{
    "username": "spaceflight_operator",
    "api_key_masked": "key_bc...4cf1",
    "tier": "free",
    "simulations_this_month": 12,
    "monthly_limit": 5000
}
```

---

### 🧪 3.4 Predict Peak CPU Temperature (AI Surrogate)
Uses the trained Random Forest emulator to predict peak temperature and burnout margins.
- **URL:** `/v1/predict` (or `/predict`)
- **Method:** `POST`
- **Headers:** `X-API-Key: <key>`
- **Body:**
```json
{
    "power": 30.0,
    "area": 0.12,
    "emissivity": 0.85
}
```
- **Response (200 OK):**
```json
{
    "max_temp_c": 71.4,
    "time_to_critical_sec": null,
    "uncertainty": 2.352,
    "ci95": [69.048, 73.752],
    "safety_reliability": 0.99998,
    "inference_mode": "AI Surrogate (Random Forest)",
    "tier": "pro"
}
```

---

### 💻 3.5 Run 6-Node Transient Solver (Physical Simulation)
Solves the dynamic lumped coupled ODE system in real time, returning the time-series trajectory.
- **URL:** `/v1/simulate` (or `/simulate`)
- **Method:** `GET`
- **Query Params:**
  * `power` (float, required): Heat generation load (W)
  * `area` (float, required): Radiator area (m²)
  * `emissivity` (float, required): Coating emissivity (ε)
  * `heat_capacity` (float, optional): CPU thermal capacity (J/K)
  * `initial_temp` (float, optional): Startup temp (K)
- **Response (200 OK):**
```json
{
    "time": [0.0, 10.0, 20.0, "..."],
    "temperature": [20.0, 20.25, 20.51, "..."],
    "max_temp_c": 71.42,
    "time_to_critical_sec": null,
    "steady_state_temp_c": 75.31,
    "nodal_temperatures": {
        "CPU": [20.0, 20.25, "..."],
        "Battery": [20.0, 20.01, "..."],
        "Payload": [20.0, 20.05, "..."],
        "Structure": [20.0, 20.02, "..."],
        "Radiator": [20.0, 19.85, "..."],
        "SolarPanels": [20.0, 20.12, "..."]
    },
    "nodal_max_temps": {
        "CPU": 71.42,
        "Battery": 35.12,
        "Payload": 42.15,
        "Structure": 38.90,
        "Radiator": 32.14,
        "Paneles": 56.40
    },
    "nodal_time_to_critical": {
        "CPU": -1.0,
        "Battery": -1.0,
        "Payload": -1.0,
        "Structure": -1.0,
        "Radiator": -1.0,
        "Paneles": -1.0
    },
    "inference_mode": "Coupled 6-Node LEO Solver (Euler + RK45)"
}
```

---

### 📄 3.6 Export Engineering PDF Report
Runs a coupled simulation and generates a publication-ready PDF report.
- **URL:** `/v1/export-report` (or `/export-report`)
- **Method:** `POST`
- **Body:**
```json
{
    "power": 30.0,
    "area": 0.12,
    "emissivity": 0.85,
    "scenario": "LEO 400km",
    "geometry": "cube",
    "case_name": "Cubesat Vuelo 3U"
}
```
- **Response (200 OK):**
Binary stream (`application/pdf`) containing the compiled ReportLab PDF document.

---

### 📊 3.7 Prometheus Metrics
Exposes internal server metrics.
- **URL:** `/v1/metrics` (or `/metrics`)
- **Method:** `GET`
- **Response (200 OK):**
```text
# HELP thermal_api_uptime_seconds Digital Twin API Server Uptime
# TYPE thermal_api_uptime_seconds counter
thermal_api_uptime_seconds 1254.2
# HELP thermal_api_calls_total Cumulative API simulation requests
# TYPE thermal_api_calls_total counter
thermal_api_calls_total 45
# HELP thermal_api_model_status Active status of neural/forest surrogates
# TYPE thermal_api_model_status gauge
thermal_api_model_status 1
```
