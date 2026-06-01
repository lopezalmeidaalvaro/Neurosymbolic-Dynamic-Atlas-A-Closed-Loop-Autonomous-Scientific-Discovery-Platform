/*
 * ==============================================================================
 * Spacecraft Thermal OS (AST-OS) - Model Predictive Control (MPC) Solver
 * File: mpc_controller.c
 * Description: Bounded grid-search MPC trajectory optimizer for flight thermal safety.
 * Author: Alvaro Lopez Almeida & Antigravity AI
 * ==============================================================================
 */

#include "mpc_controller.h"
#include <math.h>
#include <float.h>

#define Q_LEVELS 3
#define EPS_LEVELS 2

static const float Q_GRID[Q_LEVELS] = {5.0f, 15.0f, 30.0f};
static const float EPS_GRID[EPS_LEVELS] = {0.15f, 0.85f};

/*
 * Evaluates the cost function of a 5-step thermal trajectory.
 * Bounded execution: zero dynamic allocations, fixed iteration loops.
 */
void ASTOS_SolveMPC(
    float current_cpu_temp,
    float calibrated_emissivity,
    float *opt_q_cpu,
    float *opt_eps
) {
    float min_cost = FLT_MAX;
    float best_q_seq[MPC_HORIZON] = {15.0f, 15.0f, 15.0f, 15.0f, 15.0f};
    float best_eps_seq[MPC_HORIZON] = {0.85f, 0.85f, 0.85f, 0.85f, 0.85f};

    /* Physical Constants for predictive Euler step */
    float cp = 250.0f;          /* Nodal thermal capacity (Avionics Node 0) */
    float area = 0.15f;         /* Radiator area */
    float sigma = 5.67e-8f;     /* Stefan-Boltzmann */
    float t_space_k4 = 81.0f;   /* T_space^4 (Background radiation) */
    float dt = 10.0f;           /* Time step: 10s (Total Horizon: 50s) */

    /*
     * Flat loop evaluation of all possible trajectories (3^5 * 2^5 = 243 * 32 = 7776 cases).
     * This execution is deterministic, CPU pipeline friendly, and takes <0.5ms.
     */
    int32_t i0, i1, i2, i3, i4;
    int32_t j0, j1, j2, j3, j4;

    for (i0 = 0; i0 < Q_LEVELS; i0++) {
    for (i1 = 0; i1 < Q_LEVELS; i1++) {
    for (i2 = 0; i2 < Q_LEVELS; i2++) {
    for (i3 = 0; i3 < Q_LEVELS; i3++) {
    for (i4 = 0; i4 < Q_LEVELS; i4++) {
        
        for (j0 = 0; j0 < EPS_LEVELS; j0++) {
        for (j1 = 0; j1 < EPS_LEVELS; j1++) {
        for (j2 = 0; j2 < EPS_LEVELS; j2++) {
        for (j3 = 0; j3 < EPS_LEVELS; j3++) {
        for (j4 = 0; j4 < EPS_LEVELS; j4++) {
            
            float q_seq[5] = {Q_GRID[i0], Q_GRID[i1], Q_GRID[i2], Q_GRID[i3], Q_GRID[i4]};
            float eps_seq[5] = {EPS_GRID[j0], EPS_GRID[j1], EPS_GRID[j2], EPS_GRID[j3], EPS_GRID[j4]};
            
            float temp = current_cpu_temp;
            float total_cost = 0.0f;
            float prev_eps = calibrated_emissivity;
            
            /* Dynamic Forward Simulation over Horizon N = 5 */
            for (int k = 0; k < 5; k++) {
                float temp_k = temp + 273.15f; /* Convert to Kelvin */
                
                /* Euler heat balance prediction step */
                /* dT/dt = (Q_cpu - eps*sigma*Area*(T^4 - T_space^4) - Conductance*(T - T_struct)) / Cp */
                float radiation_out = eps_seq[k] * sigma * area * (powf(temp_k, 4.0f) - t_space_k4);
                float conduction_out = 1.2f * (temp - 25.0f); /* Conductive coupling to spaceframe struct */
                
                float dt_temp = (q_seq[k] - radiation_out - conduction_out) / cp;
                temp += dt_temp * dt;
                
                /* 1. Constraint Violation: CPU must never exceed 85.0C */
                if (temp >= 85.0f) {
                    total_cost += 1e7f; /* Severe penalty */
                }
                
                /* 2. Optimal Temperature Range Penalty [20, 40]C */
                if (temp > 40.0f) {
                    total_cost += (temp - 40.0f) * (temp - 40.0f) * 10.0f;
                } else if (temp < 20.0f) {
                    total_cost += (20.0f - temp) * (20.0f - temp) * 10.0f;
                }
                
                /* 3. Throttling Power Penalty (penalize choosing lower power) */
                float throttling = 30.0f - q_seq[k];
                total_cost += throttling * throttling * 5.0f;
                
                /* 4. Actuator wear penalty (penalize switching emissivity) */
                if (eps_seq[k] != prev_eps) {
                    total_cost += 15.0f;
                }
                prev_eps = eps_seq[k];
            }
            
            /* Select trajectory with the absolute minimum cost */
            if (total_cost < min_cost) {
                min_cost = total_cost;
                for (int k = 0; k < 5; k++) {
                    best_q_seq[k] = q_seq[k];
                    best_eps_seq[k] = eps_seq[k];
                }
            }
        }}}}}
    }}}}}

    /* Return the first action from the optimal predicted control sequence */
    *opt_q_cpu = best_q_seq[0];
    *opt_eps = best_eps_seq[0];
}
