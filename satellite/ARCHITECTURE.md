# AST-OS Core Architecture & Mathematical Formulations

This document registers the systems engineering architecture, thermodynamic formulations, and data flow pipelines governing the **Autonomous Spacecraft Thermal OS (AST-OS)**.

---

## 1. Multi-Node Transient Thermodynamic Formulation

The spacecraft is represented as a thermal graph network of $N$ coupled isothermal nodes. The transient energy conservation equation for each node $i$ is formulated as:

$$C_i \frac{dT_i}{dt} = Q_{\text{gen}, i} + Q_{\text{solar}, i}(t) + Q_{\text{albedo}, i}(t) + Q_{\text{earth}, i}(t) - \sum_{j \neq i} K_{ij} (T_i - T_j) - \sum_{j \neq i} R_{ij} \sigma (T_i^4 - T_j^4) - A_i \epsilon_i \sigma (T_i^4 - T_{\text{space}}^4)$$

Where:
* **$C_i$**: Thermal heat capacity of node $i$ (J/K).
* **$T_i$**: Absolute temperature of node $i$ (K).
* **$Q_{\text{gen}, i}$**: Internal electrical power dissipation (e.g., CPU, battery charge dissipation) (W).
* **$Q_{\text{solar}, i}, Q_{\text{albedo}, i}, Q_{\text{earth}, i}$**: Solar absorption, Earth reflection (albedo), and infrared Earth emission boundary fluxes (W).
* **$K_{ij}$**: Conductive coupling coefficient between nodes $i$ and $j$ (W/K).
* **$R_{ij}$**: Radiative cavity coupling factor between nodes $i$ and $j$ (dimensionless).
* **$A_i, \epsilon_i$**: Radiating area ($m^2$) and surface emissivity of node $i$ exposed to space.
* **$\sigma$**: Stefan-Boltzmann constant ($5.670 \times 10^{-8} \text{ W/m}^2\text{K}^4$).
* **$T_{\text{space}}$**: Cosmic microwave background temperature ($\approx 2.7\text{ K}$).

---

## 2. Robust Line-of-Sight Extended Kalman Filter (LOS-EKF)

To correct for dynamic structural expansions and solar pressure tilts, the Attitude Determination and Control System (ADCS) is coupled with a robust EKF solver. The state vector is modeled as:

$$x = \begin{bmatrix} q \\ \omega \\ \theta_{\text{drift}} \end{bmatrix}$$

Where $q$ is the attitude quaternion, $\omega$ is the angular velocity, and $\theta_{\text{drift}}$ is the thermal expansion bending drift vector. The discrete-time state propagation utilizes dynamic covariance weighting:

$$x_{k|k-1} = f(x_{k-1|k-1}, u_{k-1}) + w_{k-1}$$
$$P_{k|k-1} = F_{k-1} P_{k-1|k-1} F_{k-1}^T + Q_k$$

Where the transition Jacobian $F_{k-1}$ is modulated in real-time by nodal structural temperature profiles to dynamically scale gyroscope drift covariance limits under severe shadow-to-sunlight thermal shocks.

---

## 3. Failure Detection, Isolation, and Recovery (FDIR)

The onboard FDIR engine runs as an isolated high-priority real-time task. It uses analytical redundancy to classify spacecraft safety states:

1. **Active Checkers:** Monitors sensor telemetry residuals against predicted PINN emulator outputs.
2. **Dynamic Watchdog:** Modulates CPU duty cycle or triggers thermostat heaters under critical thresholds.
3. **Recovery Levels:**
   * **Level 1 (Operational):** Safe-mode CPU throttling under battery peak temperature (>60°C).
   * **Level 2 (Recovery):** Redundant sensor switching on Extended Kalman filter prediction divergence.
   * **Level 3 (Emergency):** Payload shut down, ADCS pointing optimization toward sun vectors to warm struct, and watchdog-forced hardware reset.

---

## 4. Cyber-Physical Data Ingestion Pipeline

AST-OS uses a versioned FastAPI backend acting as the bridge between telemetry datasets and Next.js React client views.

```text
  [CubeSat Hardware / TVAC Simulator] 
                │ (Dynamic telemetry files)
                ▼
      [run_thermal_pipeline.py] 
                │ (JSON Logs serialization)
                ▼
       [FastAPI backend/server] ◄───► [SQLite auth.db]
                ▲
                │ (Secure SWR HTTP Request / CORS enabled)
                ▼
     [Next.js scientific dashboard]
```

All API communications are secured via API headers (`X-API-Key`) with dynamic client rate limiting managed in memory:
* **Free Tier:** 100 requests / minute, free student evaluation key `free_student_key_abc123`.
* **Pro Tier:** 1000 requests / minute, enterprise engineering key `pro_enterprise_key_xyz987`.
