/*
 * ==============================================================================
 * Spacecraft Thermal OS (AST-OS) - Core Flight System (cFS) Application Headers
 * File: astos_app.h
 * Description: Main header file defining cFS task variables, prototypes, and structures.
 * ==============================================================================
 */

#ifndef _ASTOS_APP_H_
#define _ASTOS_APP_H_

#include "astos_msg.h"
#include "astos_tbldefs.h"
#include "mpc_controller.h"
#include <stddef.h>

/* cFS API / Service mock wrappers if building standalone, otherwise standard cFS headers */
#define ASTOS_PIPE_DEPTH       32
#define ASTOS_APP_NAME         "ASTOS_TLM_APP"

/* Command Codes (CC) */
#define ASTOS_NOOP_CC          0U
#define ASTOS_RESET_CC         1U
#define ASTOS_SETPARAM_CC      2U

/* Event IDs (EVS) conforming to Event Services */
#define ASTOS_INIT_INF_EID     1U
#define ASTOS_COMMAND_INF_EID  2U
#define ASTOS_TLM_INF_EID      3U
#define ASTOS_FDIR_WARN_EID    4U
#define ASTOS_FDIR_RECOVERY_EID 5U
#define ASTOS_ERR_EID          6U
#define ASTOS_EDAC_CORR_EID    7U
#define ASTOS_INTEG_FAIL_EID   8U
#define ASTOS_INTEG_RELOAD_EID 9U

/* Main Application State Structure */
typedef struct {
    /* Command Execution Counters */
    uint16_t                CmdCounter;
    uint16_t                ErrCounter;
    
    /* cFS Core Services Handles */
    int32_t                 CmdPipeId;
    int32_t                 TlmPipeId;
    uint32_t                TableHandle;
    
    /* Pointers to dynamic configurations */
    ASTOS_ThermalTable_t*   ThermalTablePtr;
    
    /* Active State Vectors */
    float                   NodeTemps[ASTOS_NODE_COUNT];
    float                   CalibratedEmissivity;
    float                   PredictedCpuMax;
    float                   TimeToCritical;
    
    /* Running Indicators */
    uint8_t                 FdirActive;
    uint8_t                 RedundantEkfActive;
    
    /* Control Modes (0 for PID, 1 for MPC) */
    uint8_t                 ControlMode;
    
    /* Stack base pointer for hardware exception monitors */
    uintptr_t               StackBaseAddress;
    
    /* Space packet buffers */
    ASTOS_TlmPacket_t       OutTlmPacket;
    
    /* EKF Matrices (Statically Bounded) */
    float                   EkfState;          /* Single-state parameter estimator: Emissivity */
    float                   EkfCovariance;     /* Parameter estimation covariance */
    float                   EkfProcessNoise;
    float                   EkfSensorNoise;
} ASTOS_AppData_t;

/*
 * ==============================================================================
 * Standard Core Flight cFS API Prototypes
 * ==============================================================================
 */

/* Main task entry point */
void ASTOS_AppMain(void);

/* Application initialization routines */
int32_t ASTOS_AppInit(void);

/* Message loop handler */
void ASTOS_ProcessCommandPacket(const CFE_SB_Msg_t* MsgPtr);
void ASTOS_ProcessTelemetryPacket(const CFE_SB_Msg_t* MsgPtr);

/* Physics core calculation steps */
void ASTOS_RunThermalInference(const float input_power[1], float output_temps[2]);
void ASTOS_RunEfkStateEstimation(float observed_temp, float input_power);
void ASTOS_TriggerFdirCountermeasures(void);

/* Mock executive restart interface */
void CFE_ES_RestartApp(uint32_t Reason);

#endif /* _ASTOS_APP_H_ */
