# AST-OS Mission Dossier

## 1. Executive Summary
This dossier outlines the orbital mission profiles, flight envelopes, attitude control couplings, and flight safety operation protocols supported by AST-OS for aerospace deployments.

## 2. Purpose
The purpose of the mission profiling system is to predict thermal envelopes across diverse orbit geometries, verify instrument safety bounds, and ensure compliance with space operations communications standards.

## 3. Architecture
The mission operations logic is organized hierarchically:

```
   [Orbit Selection: LEO / SSO]
                |
                v
   [Attitude Envelopes & Pointing]
                |
                v
  [ECSS PUS Telemetry Codecs]
                |
                v
  [Safe Mode State Machine Trigger]
```

*   **Orbit Simulator**: Generates transient solar flux loads.
*   **Thermal Envelope Validator**: Computes instrument safety boundaries.
*   **Operations Core**: Encodes and decodes telemetry packages.

## 4. Methodology
*   **Low Earth Orbit (LEO) Runs**: Models solar radiation, Earth albedo, and planetary infrared flux. Eclipse periods (average 35 minutes per 90-minute orbit) are modeled to evaluate structural cool-down transitions.
*   **Sun-Synchronous Orbit (SSO) Runs**: Evaluates stable constant-beta angles to optimize heater duty cycles.
*   **Attitude Coupling**: Integrates satellite orientation sweeps (nadir-pointing vs. sun-pointing) to identify attitude-pointing envelopes that prevent payload camera overheating.

## 5. Results
*   **Eclipse Power Balancing**: Heater duty cycle configurations successfully stabilized battery pack temperatures within $+5^\circ\text{C}$ to $+35^\circ\text{C}$ across LEO eclipse boundaries.
*   **Array Thermal Coupling**: Solar array generation curves are accurately coupled with structural thermal expansion coefficients, reducing power output prediction uncertainty by $15\%$.

## 6. Validation
*   **ECSS Standard Codecs**: Space telemetry packets conform to the ECSS-compliant PUS standards (Service 3 for diagnostics, Service 5 for event reporting).
*   **Safe Mode Safety Triggers**: If payload or battery sensor readings diverge from digital twin state predictions by more than **$5.0^\circ\text{C}$** continuously for $120$ seconds, the spacecraft bus automatically triggers Safe Mode state recovery protocols.

## 7. Limitations
*   **Orbital Perturbation Simplicity**: The solar flux simulator uses a static orbital model and does not account for micro-drag or solar wind variations which can affect albedo coefficients.
*   **Structural Expansion Limits**: Linear thermal expansion coefficients are assumed, which may diverge under severe thermal shocks ($>150^\circ\text{C}$ deltas).

## 8. Future Work
*   **Lagrangian Points Orbit Profiling**: Expanding orbital thermal load models to Lagrange points (L1, L2) to support deep-space telescope missions.
*   **Dynamic Albedo mapping**: Interfacing with live earth-science databases to ingest real-time regional cloud cover and albedo changes.

## 9. Source Documents
*   [ASTOS_MISSION_DOSSIER.md (Original)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/ASTOS_MISSION_DOSSIER.md)
*   [satellite/ROADMAP.md (Consolidated)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/ROADMAP.md)
