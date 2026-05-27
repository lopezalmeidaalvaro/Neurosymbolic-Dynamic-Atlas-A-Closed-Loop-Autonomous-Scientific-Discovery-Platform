# Commercial API Technical Documentation

This document describes the REST API endpoints exposed by the Cubesat Thermodynamic Digital Twin platform.

## Endpoints

### 1. Predict Peak CPU Temperature
- **URL**: `/predict`
- **Method**: `POST`
- **Body**:
```json
{
    "api_key": "pro_enterprise_key_xyz987",
    "power": 15.0,
    "area": 0.15,
    "emissivity": 0.85
}
```
- **Response**:
```json
{
    "status": "success",
    "timestamp": 1779836372.1,
    "tier": "pro",
    "max_temp": 72.4,
    "uncertainty": 1.8,
    "ci95": [68.8, 76.0],
    "safety_reliability": 0.99998
}
```

### 2. Optimize Radiator Geometry
- **URL**: `/optimize`
- **Method**: `POST`
- **Body**:
```json
{
    "api_key": "pro_enterprise_key_xyz987"
}
```
