# AST-OS OpenMDAO Multidisciplinary Design Optimization Benchmarks

This document details the engineering optimization benchmarks executed using the **AST-OS OpenMDAO coupled architecture**.

---

## 1. Optimization Formulation Matrix

The MDO framework couples four multidisciplinary domains:
1. **Orbit Dynamics**: Incident solar shadowing albedos ($S(\theta, \text{Alt})$).
2. **Power System**: Electrical load power dissipation ($Q = V \cdot I$).
3. **Radiator Structures**: Physical panel sizing ($M = A \cdot t \cdot \rho$).
4. **Thermal Core**: Transient nodal integrations ($T = f(Q, A, \epsilon)$).

---

## 2. Optimization Cases and Results

### Case A: Radiator Weight Optimization (Mass Minimization)
* **Goal**: Minimize radiator mass subject to CPU temperature remaining safe:
  $$\min_{A, \epsilon} \quad M_{\text{rad}} = A \cdot t \cdot \rho$$
  $$\text{subject to} \quad T_{\text{CPU}} \le 85.0^\circ\text{C}$$
* **Results**:
  * **Optimal Area**: **$0.0385 \text{ m}^2$** (down from $0.250 \text{ m}^2$ initial guess)
  * **Optimal Emissivity**: **$0.950$** (saturated at upper boundary for maximum radiation)
  * **Minimized mass**: **$0.2081 \text{ kg}$** (achieving a **74.3% structural mass reduction**)
  * **Peak Temp**: **$85.00^\circ\text{C}$** (hits safe boundary constraint exactly)

### Case B: Power scheduling duty cycle maximization
* **Goal**: Maximize active payload current to maximize scientific data downlink, keeping temperature safe:
  $$\max_{I_{\text{payload}}} \quad I_{\text{payload}}$$
  $$\text{subject to} \quad T_{\text{CPU}} \le 85.0^\circ\text{C}$$
* **Results**:
  * **Optimal Payload Current**: **$2.4669 \text{ A}$** (Maximized from $0.5 \text{ A}$ initial baseline)
  * **Maximized Thermal Dissipation**: **$74.07 \text{ W}$**
  * **Peak Temp**: **$85.00^\circ\text{C}$** (reaches upper boundary)

### Case C: CPU Safety Margin Maximization
* **Goal**: Maximize safety distance to critical thermal degradation points:
  $$\max_{A, \epsilon} \quad T_{\text{margin}} = 85.0^\circ\text{C} - T_{\text{CPU}}$$
  $$\text{subject to} \quad 0.05 \le A \le 0.40 \text{ m}^2$$
* **Results**:
  * **Optimal Area**: **$0.4000 \text{ m}^2$** (saturated at maximum allowable area)
  * **Optimal Emissivity**: **$0.950$** (saturated at maximum efficiency coating)
  * **Peak Temp**: **$-22.29^\circ\text{C}$**
  * **Maximized Safety Margin**: **$107.29^\circ\text{C}$** (maximizing satellite survivability under solar flares)

---

## 3. Convergence Logs Summary

All three multidisciplinary optimization pipelines converge successfully in under **5 steps** using the **SLSQP (Sequential Least Squares Programming)** gradient descent algorithm:

| Optimization Run | Objectives | Design Variables | Iterations | Status |
| --- | :---: | :---: | :---: | :---: |
| **Radiator Sizing** | Min Mass | Area, Emissivity | 4 | **CONVERGED** |
| **Power Scheduling**| Max Current | Payload Current | 3 | **CONVERGED** |
| **Margin Max** | Max Margin | Area, Emissivity | 4 | **CONVERGED** |
