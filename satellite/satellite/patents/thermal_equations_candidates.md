# Spacecraft Radiator Design - Discovered Equations Candidates
**Date:** 2026-05-27

This document outlines the closed-form analytical equations discovered via symbolic regression, modeling LEO satellite radiator thermodynamical properties. These candidates represent patentable formulations for digital twin physics accelerators.

## Discovered Candidates

### 1. Analytical Steady State Temperature ($T_{\text{eq}}$)
- **Symbolic Representation:** `$((power / (emissivity * 5.670e-08 * area * 1.0000)) + 53.1)**0.25 - 273.15 + 0.0000$`
- **Physical Interpretation:** Stefan-Boltzmann balance between spacecraft power generation and radiation loss to space at 2.7K.

### 2. Maximum Simulation Temperature ($T_{\text{max}}$)
- **Symbolic Representation:** `$0.4370 * ((power / (emissivity * 5.670e-08 * area))**0.25 - 273.15) + -0.2645 * power + 46.2136$`
- **Physical Interpretation:** Fits the peak transient temperature of the orbit. Takes into account thermal capacity scaling.

### 3. Time to Critical Temperature ($t_{\text{crit}}$)
- **Symbolic Representation:** `$0.9221 * 32500.0 / (power - 6.725e-08 * emissivity * area * 1.116e10)$`
- **Physical Interpretation:** Evaluates the time in seconds to reach the avionics critical threshold ($85^\circ\text{C}$) under thermal stress.

### 4. Mean Cooling Rate ($CR$)
- **Symbolic Representation:** `$1.0000 * (emissivity * 5.670e-08 * area * 8.1e9) / 500.0 + 0.0000$`
- **Physical Interpretation:** Governs the thermal dissipation rate in vacuum when internal systems are idle.
