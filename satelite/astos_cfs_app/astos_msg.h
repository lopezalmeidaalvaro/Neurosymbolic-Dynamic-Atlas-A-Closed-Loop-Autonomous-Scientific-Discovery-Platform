/*
 * ==============================================================================
 * Spacecraft Thermal OS (AST-OS) - Core Flight System (cFS) Application Headers
 * File: astos_msg.h
 * Description: Defines CCSDS command and telemetry packets conforming to cFS Standards.
 * ==============================================================================
 */

#ifndef _ASTOS_MSG_H_
#define _ASTOS_MSG_H_

#include <stdint.h>

/*
 * cFS standard message headers
 * Usually imported from cfe_sb.h, represented here as byte arrays matching 
 * CCSDS 133.0-B-1 space packet standards.
 */
typedef struct {
    uint8_t   hdr[6];      /* CCSDS Primary Header: Version, Type, APID, Seq, Length */
    uint8_t   sec[4];      /* Secondary Header: Time stamp or flags */
} CFE_SB_Msg_t;

typedef struct {
    uint8_t   hdr[6];      /* CCSDS Primary Header */
    uint8_t   sec[2];      /* Secondary Header: Command code, checksum */
} CFE_SB_CmdHdr_t;

/*
 * ==============================================================================
 * Command Packet Structures
 * ==============================================================================
 */

/* Commands with no arguments (e.g., ASTOS_NOOP_CC, ASTOS_RESET_CC) */
typedef struct {
    CFE_SB_CmdHdr_t  CmdHeader;
} ASTOS_NoArgsCmd_t;

/* Command to dynamically adjust safety thermal threshold limits */
typedef struct {
    CFE_SB_CmdHdr_t  CmdHeader;
    float            CpuSafeLimit;     /* New temperature threshold in °C (Nominal: 85.0f) */
    float            RadiatorArea;     /* Dynamic area adjustments */
} ASTOS_SetParamCmd_t;

/*
 * ==============================================================================
 * Telemetry Packet Structures
 * ==============================================================================
 */

/* Main Telemetry Packet published by the AST-OS cFS Application */
typedef struct {
    CFE_SB_Msg_t     TlmHeader;
    
    /* Telemetry Payload States */
    float            CpuTemperature;        /* Active Node 0 (Avionics) in °C */
    float            BatteryTemperature;    /* Active Node 1 (EPS Battery) in °C */
    float            PayloadTemperature;    /* Active Node 2 (Optics/Payload) in °C */
    float            StructureTemperature;  /* Active Node 3 (Spaceframe) in °C */
    float            RadiatorTemperature;   /* Active Node 4 (Radiator Panel) in °C */
    
    /* Dynamic Inference Core Values */
    float            PredictedCpuMaxTemp;   /* Estimated peak in °C from MLP/ODE surrogate */
    float            CalibratedEmissivity;  /* Online EKF state estimation value */
    float            TimeToCritical;        /* Time left before CPU limit in seconds (-1.0f if safe) */
    
    /* System FDIR Health Indicators */
    uint8_t          FdirActiveFlag;        /* 1 = Throttling Countermeasures active; 0 = Nominal */
    uint8_t          RedundantEkfActive;    /* 1 = Switched to backup estimation node; 0 = Normal */
    uint8_t          ErrorCounters;         /* Incremental packet drop/outlier register */
    uint8_t          Spare[1];              /* Byte alignment padding */
} ASTOS_TlmPacket_t;

#endif /* _ASTOS_MSG_H_ */
