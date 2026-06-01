/*
 * ==============================================================================
 * Spacecraft Thermal OS (AST-OS) - Model Predictive Control (MPC) Header
 * File: mpc_controller.h
 * Description: Declares the lightweight MPC solver variables and routines.
 * ==============================================================================
 */

#ifndef _MPC_CONTROLLER_H_
#define _MPC_CONTROLLER_H_

#include <stdint.h>

#define MPC_HORIZON 5

/*
 * Dynamic control mode status variables
 */
#define ASTOS_CONTROL_MODE_PID 0U
#define ASTOS_CONTROL_MODE_MPC 1U

/* Command Code to toggle MPC/PID control mode */
#define ASTOS_SET_MPC_MODE_CC  3U

/*
 * Solves the constrained model predictive control problem over horizon N=5.
 * Evaluates candidates discretely to minimize CPU power throttling while
 * maintaining temperatures within optimal range [20, 40]°C.
 * 
 * WCET is bounded under 1ms.
 */
void ASTOS_SolveMPC(
    float current_cpu_temp,
    float calibrated_emissivity,
    float *opt_q_cpu,
    float *opt_eps
);

#endif /* _MPC_CONTROLLER_H_ */
