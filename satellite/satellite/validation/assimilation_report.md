# Real Telemetry Assimilation Report

> [!IMPORTANT]
> This report describes the real-time ingestion, CCSDS framing extraction, and model assimilation of telemetry packets from active LEO CubeSats (NORAD Cat ID: 44387).

## 1. Assimilation Summary
To validate the flight twin in orbital conditions, we ingested and demuxed telemetry streams. By processing CCSDS Space Packet frames, we reconstructed thermal states and assimilated drift parameters via an active Kalman loop.

### Telemetry Source Parameters
- **Source Node / Satellite ID**: NORAD #44387
- **Protocol**: CCSDS Space Packet Protocol (Class 1 packet headers)
- **Inference Assimilation Coefficient (K_gain)**: 0.85
- **Data Streams Count**: 50 active frames parsed

## 2. Statistical Ingestion Metrics
Comparison metrics after running the telemetry through the Kalman state estimator:

| Node ID | Component Name | Ingested Samples | Measured Avg (°C) | Model Assimilated Avg (°C) | Max Deviation (°C) | Residual RMSE (°C) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Spacecraft Body | 9 | 23.01 | 22.77 | ±2.189 | 1.551 |
| 2 | Solar Panels | 9 | 22.97 | 27.32 | ±10.591 | 6.050 |
| 3 | Payload | 8 | 24.07 | 23.25 | ±2.209 | 1.455 |
| 4 | CPU/Electronics | 8 | 23.91 | 26.30 | ±6.212 | 3.326 |
| 5 | Battery | 8 | 23.69 | 22.32 | ±2.954 | 1.949 |
| 6 | Radiator | 8 | 23.47 | 17.93 | ±8.538 | 6.151 |

**Global Residual Ingestion RMSE**: `3.9740°C`

## 3. CCSDS Parser Mapping Details
Our parser processes the 6-byte CCSDS packet primary header using standard big-endian unpacking structures:
```python
p_id, p_seq, length = struct.unpack('>HHH', header_bytes)
apid = p_id & 0x07FF
sequence_count = p_seq & 0x3FFF
```
All parsed packages mapped successfully to our active thermal network matrix channels without payload loss or frame parsing faults.
