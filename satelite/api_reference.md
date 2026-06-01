# Spacecraft Thermal OS (AST-OS) - SaaS REST API Reference Manual

This manual details the versioned, production-grade endpoints, inputs/outputs Pydantic schemas, and header mappings for AST-OS, conforming to the OpenAPI standard.

---

## 1. Authentication & Security Mappings

Every secure endpoint requires credentials passed through Headers:
* **API Key Header**: `X-API-Key: <your_api_key>`
* **JWT Header**: `Authorization: Bearer <your_jwt_token>`

---

## 2. API Endpoints Reference

### A. Authentication Subsystem

#### `POST /v1/auth/register`
* **Description**: Registers a new customer billing profile and returns a safe API Key.
* **Input Schema (`RegisterRequest`)**:
```json
{
  "username": "satellite_operator",
  "email": "operator@spaceframe.org",
  "password": "spacepassword123"
}
```
* **Output Schema**:
```json
{
  "status": "success",
  "message": "User registered successfully.",
  "api_key": "key_e45a7b8c...",
  "tier": "free",
  "rate_limit": "100 req/day"
}
```

#### `POST /v1/auth/login`
* **Description**: Verifies credentials and generates a base64url signed JWT access token.
* **Input Schema (`LoginRequest`)**:
```json
{
  "username": "satellite_operator",
  "password": "spacepassword123"
}
```
* **Output Schema**:
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "tier": "free"
}
```

---

### B. Core Thermodynamic & Autonomy Subsystems

#### `POST /v1/simulate`
* **Description**: Executes a high-fidelity numerical ODE transient thermal simulation of 6-node LEO spacecraft frames.
* **Input Schema (`SimulationConfig`)**:
```json
{
  "power": 30.0,
  "area": 0.15,
  "emissivity": 0.85,
  "heat_capacity": 500.0,
  "initial_temp": 25.0
}
```
* **Output Schema**:
```json
{
  "status": "success",
  "time": [0.0, 36.36, 72.72, "..."],
  "temperatures": [25.0, 25.42, 25.83, "..."],
  "max_temp_c": 55.12,
  "time_to_critical_sec": -1.0,
  "nodal_temperatures": {
    "CPU": [25.0, 25.42, "..."],
    "Battery": [16.25, 16.52, "..."],
    "Payload": [21.25, 21.60, "..."]
  }
}
```

#### `POST /v1/thermal/predict`
* **Description**: Evaluates peak CPU core temperatures instantly using the validated physical surrogate equations.
* **Input Schema (`PredictionConfig`)**:
```json
{
  "power": 15.0,
  "area": 0.15,
  "emissivity": 0.85
}
```
* **Output Schema**:
```json
{
  "status": "success",
  "max_temp_c": 52.41,
  "time_to_critical_sec": -1.0,
  "safety_margin_c": 32.59
}
```

#### `POST /v1/fault-detect`
* **Description**: Runs in-flight checks over EKF telemetry states to detect SEU memory corruptions or radiator aging decays.
* **Input Schema (`TelemetryConfig`)**:
```json
{
  "observed_temp": 86.2,
  "calibrated_emissivity": 0.35,
  "bitflip_count": 12
}
```
* **Output Schema**:
```json
{
  "status": "success",
  "fault_detected": true,
  "primary_action": "CFE_ES_RestartApp / Reload Golden flash copy",
  "warnings": [
    "CRITICAL: CPU temperature exceeds safety boundary.",
    "WARNING: Radiator structural emissivity decay detected.",
    "CRITICAL: Memory bitflip counts exceed limits."
  ]
}
```

#### `POST /v1/mission/run`
* **Description**: Performs discrete mission planning to optimize orbital task scheduling without violating thermal limits.
* **Input Schema (`MissionConfig`)**:
```json
{
  "tasks": [
    {"name": "Earth_Imaging", "duration": 120.0, "power_draw": 15.0, "priority": 5},
    {"name": "Payload_Deep_Space", "duration": 500.0, "power_draw": 200.0, "priority": 10}
  ]
}
```
* **Output Schema**:
```json
{
  "status": "success",
  "scheduled_tasks": ["Earth_Imaging"],
  "skipped_tasks": ["Payload_Deep_Space"],
  "temperature_projection": [25.0, 14.89]
}
```

#### `POST /v1/telemetry/analyze`
* **Description**: Ingests raw telemetry, executes median outlier filters to reject bitflips, and applies EMA noise smoothers.
* **Input Schema (`TelemetryAnalysisRequest`)**:
```json
{
  "raw_cpu_temperatures": [35.2, 35.8, 70.5, 36.1, 35.9]
}
```
* **Output Schema**:
```json
{
  "status": "success",
  "raw_temperatures": [35.2, 35.8, 70.5, 36.1, 35.9],
  "cleaned_temperatures": [35.2, 35.8, 35.8, 36.1, 35.9],
  "smoothed_temperatures": [35.2, 35.38, 35.51, 35.68, 35.75]
}
```

---

### C. Billing Subsystem

#### `POST /v1/stripe/checkout`
* **Description**: Spawns a secure Stripe Checkout Session returning the payment URL.
* **Input Schema (`CheckoutSessionConfig`)**:
```json
{
  "email": "customer@spaceframe.org",
  "plan": "Professional"
}
```
* **Output Schema**:
```json
{
  "status": "success",
  "session_id": "cs_test_a1b2...",
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_a1b2..."
}
```
