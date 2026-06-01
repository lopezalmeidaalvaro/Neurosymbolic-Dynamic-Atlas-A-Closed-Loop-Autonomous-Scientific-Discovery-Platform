/*
 * ==============================================================================
 * Spacecraft Thermal OS (AST-OS) - Core Flight System (cFS) Application Headers
 * File: astos_tbldefs.h
 * Description: Defines cFS Table Service structures for configurable thermal parameters.
 * ==============================================================================
 */

#ifndef _ASTOS_TBLDEFS_H_
#define _ASTOS_TBLDEFS_H_

#include <stdint.h>

#define ASTOS_NODE_COUNT 5

/*
 * Structure for the dynamic parameter table managed via cFS Table Services.
 * Allows flight operators to tune thermal parameters in-flight without code flashing.
 */
typedef struct {
    /* Nodal Thermal Capacities (J/K) */
    float   Capacity[ASTOS_NODE_COUNT];
    
    /* Surface Areas (m²) */
    float   Area[ASTOS_NODE_COUNT];
    
    /* Initial Surface Emissivities */
    float   Emissivity[ASTOS_NODE_COUNT];
    
    /* Maximum Temperature Limits (°C) before triggering critical FDIR events */
    float   MaxSafeTempLimit[ASTOS_NODE_COUNT];
    
    /* Conduction Couplings Matrix (k_ij) represent cross-conduction */
    float   ConductionCoupling[ASTOS_NODE_COUNT][ASTOS_NODE_COUNT];
    
    /* Calibration offsets */
    float   EfkCovarianceNoise;
    float   SolarFluxConstant;
} ASTOS_ThermalTable_t;

#endif /* _ASTOS_TBLDEFS_H_ */
