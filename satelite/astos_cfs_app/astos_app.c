/*
 * ==============================================================================
 * Spacecraft Thermal OS (AST-OS) - Core Flight System (cFS) Application Implementation
 * File: astos_app.c
 * Description: Hardened flight application featuring EDAC, SHA-256, exceptions and MPC.
 * Author: Alvaro Lopez Almeida & Antigravity AI
 * ==============================================================================
 */

#include "astos_app.h"
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <math.h>

/* Global Application State Data */
ASTOS_AppData_t  g_ASTOS_AppData;

/* Running simulated execution status */
static uint8_t g_cFS_Running = 1U;

/*
 * ==============================================================================
 * Standard SHA-256 Self-Contained Implementation
 * Bounded memory, no dynamic allocations.
 * ==============================================================================
 */

typedef struct {
    uint32_t state[8];
    uint32_t count[2];
    uint8_t  buf[64];
} ASTOS_SHA256_Ctx_t;

#define ROTR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define Ch(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define Maj(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define Sigma0(x) (ROTR(x, 2) ^ ROTR(x, 13) ^ ROTR(x, 22))
#define Sigma1(x) (ROTR(x, 6) ^ ROTR(x, 11) ^ ROTR(x, 25))
#define sigma0(x) (ROTR(x, 7) ^ ROTR(x, 18) ^ ((x) >> 3))
#define sigma1(x) (ROTR(x, 17) ^ ROTR(x, 19) ^ ((x) >> 10))

static const uint32_t SHA256_K[64] = {
    0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U, 0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
    0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U, 0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
    0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU, 0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
    0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U, 0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
    0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U, 0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
    0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U, 0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
    0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U, 0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
    0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U, 0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U
};

void ASTOS_SHA256_Init(ASTOS_SHA256_Ctx_t *ctx) {
    ctx->state[0] = 0x6a09e667U;
    ctx->state[1] = 0xbb67ae85U;
    ctx->state[2] = 0x3c6ef372U;
    ctx->state[3] = 0xa54ff53aU;
    ctx->state[4] = 0x510e527fU;
    ctx->state[5] = 0x9b05688cU;
    ctx->state[6] = 0x1f83d9abU;
    ctx->state[7] = 0x5be0cd19U;
    ctx->count[0] = 0U;
    ctx->count[1] = 0U;
}

static void ASTOS_SHA256_Transform(uint32_t state[8], const uint8_t data[64]) {
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t e = state[4], f = state[5], g = state[6], h = state[7];
    uint32_t w[64];
    int32_t i;

    for (i = 0; i < 16; i++) {
        w[i] = ((uint32_t)data[i * 4] << 24) | ((uint32_t)data[i * 4 + 1] << 16) |
               ((uint32_t)data[i * 4 + 2] << 8) | ((uint32_t)data[i * 4 + 3]);
    }
    for (i = 16; i < 64; i++) {
        w[i] = sigma1(w[i - 2]) + w[i - 7] + sigma0(w[i - 15]) + w[i - 16];
    }

    for (i = 0; i < 64; i++) {
        uint32_t t1 = h + Sigma1(e) + Ch(e, f, g) + SHA256_K[i] + w[i];
        uint32_t t2 = Sigma0(a) + Maj(a, b, c);
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }

    state[0] += a; state[1] += b; state[2] += c; state[3] += d;
    state[4] += e; state[5] += f; state[6] += g; state[7] += h;
}

void ASTOS_SHA256_Update(ASTOS_SHA256_Ctx_t *ctx, const uint8_t *data, size_t len) {
    size_t i, index, partlen;
    index = (ctx->count[0] >> 3) & 63;
    ctx->count[0] += (uint32_t)(len << 3);
    if (ctx->count[0] < (len << 3)) {
        ctx->count[1]++;
    }
    ctx->count[1] += (uint32_t)(len >> 29);
    partlen = 64 - index;

    if (len >= partlen) {
        memcpy(&ctx->buf[index], data, partlen);
        ASTOS_SHA256_Transform(ctx->state, ctx->buf);
        for (i = partlen; i + 63 < len; i += 64) {
            ASTOS_SHA256_Transform(ctx->state, &data[i]);
        }
        index = 0;
    } else {
        i = 0;
    }
    memcpy(&ctx->buf[index], &data[i], len - i);
}

void ASTOS_SHA256_Final(ASTOS_SHA256_Ctx_t *ctx, uint8_t hash[32]) {
    uint8_t finalcount[8];
    int32_t i;
    for (i = 0; i < 8; i++) {
        finalcount[i] = (uint8_t)((ctx->count[i >= 4 ? 0 : 1] >> ((3 - (i & 3)) * 8)) & 255);
    }
    uint8_t pad[64];
    memset(pad, 0, 64);
    pad[0] = 0x80;
    
    size_t index = (ctx->count[0] >> 3) & 63;
    ASTOS_SHA256_Update(ctx, pad, index < 56 ? 56 - index : 120 - index);
    ASTOS_SHA256_Update(ctx, finalcount, 8);

    for (i = 0; i < 8; i++) {
        hash[i * 4]     = (uint8_t)((ctx->state[i] >> 24) & 255);
        hash[i * 4 + 1] = (uint8_t)((ctx->state[i] >> 16) & 255);
        hash[i * 4 + 2] = (uint8_t)((ctx->state[i] >> 8) & 255);
        hash[i * 4 + 3] = (uint8_t)(ctx->state[i] & 255);
    }
}

/*
 * ==============================================================================
 * Hamming(7,4) EDAC Static Memory Protection Core
 * ==============================================================================
 */

static uint8_t hamming_encode_nibble(uint8_t nibble) {
    uint8_t d0 = (nibble >> 0) & 1U;
    uint8_t d1 = (nibble >> 1) & 1U;
    uint8_t d2 = (nibble >> 2) & 1U;
    uint8_t d3 = (nibble >> 3) & 1U;

    uint8_t p0 = d0 ^ d1 ^ d3;
    uint8_t p1 = d0 ^ d2 ^ d3;
    uint8_t p2 = d1 ^ d2 ^ d3;

    return (p0 << 0) | (p1 << 1) | (d0 << 2) | (p2 << 3) | (d1 << 4) | (d2 << 5) | (d3 << 6);
}

static uint8_t hamming_decode_nibble(uint8_t codeword, uint8_t *corrected_flag) {
    uint8_t p0 = (codeword >> 0) & 1U;
    uint8_t p1 = (codeword >> 1) & 1U;
    uint8_t d0 = (codeword >> 2) & 1U;
    uint8_t p2 = (codeword >> 3) & 1U;
    uint8_t d1 = (codeword >> 4) & 1U;
    uint8_t d2 = (codeword >> 5) & 1U;
    uint8_t d3 = (codeword >> 6) & 1U;

    uint8_t s0 = p0 ^ d0 ^ d1 ^ d3;
    uint8_t s1 = p1 ^ d0 ^ d2 ^ d3;
    uint8_t s2 = p2 ^ d1 ^ d2 ^ d3;

    uint8_t syndrome = s0 | (s1 << 1) | (s2 << 2);

    if (syndrome > 0U) {
        /* Correct single bit flip */
        codeword ^= (1U << (syndrome - 1U));
        *corrected_flag = 1U;

        /* Re-extract from corrected codeword */
        d0 = (codeword >> 2) & 1U;
        d1 = (codeword >> 4) & 1U;
        d2 = (codeword >> 5) & 1U;
        d3 = (codeword >> 6) & 1U;
    }

    return d0 | (d1 << 1) | (d2 << 2) | (d3 << 3);
}

static void hamming_encode_byte(uint8_t data_byte, uint8_t encoded[2]) {
    encoded[0] = hamming_encode_nibble(data_byte & 0x0FU);
    encoded[1] = hamming_encode_nibble((data_byte >> 4) & 0x0FU);
}

static uint8_t hamming_decode_byte(const uint8_t encoded[2], uint32_t *corrected_counter) {
    uint8_t low_corr = 0U;
    uint8_t high_corr = 0U;

    uint8_t low_nib = hamming_decode_nibble(encoded[0], &low_corr);
    uint8_t high_nib = hamming_decode_nibble(encoded[1], &high_corr);

    *corrected_counter += (low_corr + high_corr);
    return low_nib | (high_nib << 4);
}

/*
 * ==============================================================================
 * Model Parameter Mapping and Pre-Encoded Segment
 * Total parameters: 18 floats = 72 raw bytes -> 144 encoded bytes.
 * ==============================================================================
 */

#define RAW_WEIGHTS_SIZE 72
#define ENCODED_WEIGHTS_SIZE 144

/* Original PyTorch trained weights baseline */
static const float GOLDEN_WEIGHTS_FLOAT[18] = {
    0.58f, -0.34f, 0.82f, -0.12f,  /* FC1 Weights */
    0.1f, -0.05f, 0.22f, 0.15f,    /* FC1 Biases */
    0.95f, -0.2f, 0.6f, 0.1f,      /* FC2 Weights */
    -0.15f, 0.72f, -0.1f, 0.3f,    /* FC2 Weights Layer 2 */
    -0.25f, 0.08f                  /* FC2 Biases */
};

/* Gold read-only copy in Simulated Flash Segment */
static uint8_t GOLDEN_WEIGHTS_ENCODED[ENCODED_WEIGHTS_SIZE];
static uint8_t GOLDEN_HASH_SHA256[32];

/* Active RAM segment subject to space radiation single-event upsets (SEU) */
static uint8_t ACTIVE_RAM_ENCODED[ENCODED_WEIGHTS_SIZE];

/* Local decoded active floats used by inference core */
static float g_Active_FC1_WEIGHTS[4][1];
static float g_Active_FC1_BIASES[4];
static float g_Active_FC2_WEIGHTS[2][4];
static float g_Active_FC2_BIASES[2];

/* Helper to initialize EDAC and hashes at startup */
static void ASTOS_InitializeMemoryProtection(void) {
    uint8_t raw_bytes[RAW_WEIGHTS_SIZE];
    memcpy(raw_bytes, GOLDEN_WEIGHTS_FLOAT, RAW_WEIGHTS_SIZE);

    /* 1. Calculate Golden SHA-256 Hash */
    ASTOS_SHA256_Ctx_t sha_ctx;
    ASTOS_SHA256_Init(&sha_ctx);
    ASTOS_SHA256_Update(&sha_ctx, raw_bytes, RAW_WEIGHTS_SIZE);
    ASTOS_SHA256_Final(&sha_ctx, GOLDEN_HASH_SHA256);

    /* 2. Encode all bytes into Golden Flash */
    for (int32_t i = 0; i < RAW_WEIGHTS_SIZE; i++) {
        hamming_encode_byte(raw_bytes[i], &GOLDEN_WEIGHTS_ENCODED[2 * i]);
    }

    /* 3. Load active RAM */
    memcpy(ACTIVE_RAM_ENCODED, GOLDEN_WEIGHTS_ENCODED, ENCODED_WEIGHTS_SIZE);
}

/*
 * ==============================================================================
 * cFS Core Services Mock Wrappers (Exception & Logging Endpoints)
 * ==============================================================================
 */

int32_t CFE_ES_RegisterApp(void) {
    printf("[cFS ES] Application registered: %s (PID: 1042)\n", ASTOS_APP_NAME);
    return 0;
}

int32_t CFE_EVS_Register(const void* Filters, uint16_t NumFilters, uint16_t FilterScheme) {
    (void)Filters; (void)NumFilters; (void)FilterScheme;
    printf("[cFS EVS] Event services successfully registered with filters.\n");
    return 0;
}

int32_t CFE_EVS_SendEvent(uint16_t EventID, uint16_t EventType, const char* Format, ...) {
    (void)EventType;
    va_list args;
    va_start(args, Format);
    printf("[cFS EVENT ID %d] ", EventID);
    vprintf(Format, args);
    printf("\n");
    va_end(args);
    return 0;
}

int32_t CFE_SB_CreatePipe(int32_t* PipeIdPtr, uint16_t Depth, const char* PipeName) {
    *PipeIdPtr = 1;
    printf("[cFS SB] Software Bus pipe created: %s, Depth: %d\n", PipeName, Depth);
    return 0;
}

int32_t CFE_SB_Subscribe(uint16_t MsgId, int32_t PipeId) {
    printf("[cFS SB] Pipe %d subscribed to Message ID: 0x%04X\n", PipeId, MsgId);
    return 0;
}

int32_t CFE_SB_SendMsg(CFE_SB_Msg_t* MsgPtr) {
    (void)MsgPtr;
    return 0;
}

int32_t CFE_TBL_Register(uint32_t* TblHandlePtr, const char* Name, uint32_t Size, uint16_t Flags, void* Callback) {
    *TblHandlePtr = 42U;
    (void)Size; (void)Flags; (void)Callback;
    printf("[cFS TBL] Registered table '%s' (Handle: %d)\n", Name, *TblHandlePtr);
    return 0;
}

int32_t CFE_TBL_GetAddress(void** TblPtr, uint32_t TblHandle) {
    static ASTOS_ThermalTable_t static_table = {
        .Capacity = {200.0f, 500.0f, 400.0f, 1000.0f, 300.0f},
        .Area = {0.01f, 0.02f, 0.01f, 0.10f, 0.15f},
        .Emissivity = {0.1f, 0.1f, 0.2f, 0.3f, 0.85f},
        .MaxSafeTempLimit = {85.0f, 60.0f, 45.0f, 80.0f, 90.0f},
        .ConductionCoupling = {
            {0.0f, 1.2f, 0.5f, 0.8f, 0.0f},
            {1.2f, 0.0f, 0.4f, 0.4f, 0.0f},
            {0.5f, 0.4f, 0.0f, 0.8f, 0.0f},
            {0.8f, 0.4f, 0.8f, 0.0f, 2.5f},
            {0.0f, 0.0f, 0.0f, 2.5f, 0.0f}
        },
        .EfkCovarianceNoise = 0.001f,
        .SolarFluxConstant = 1361.0f
    };
    
    if (TblHandle == 42U) {
        *TblPtr = &static_table;
        return 0;
    }
    return -1;
}

uint8_t CFE_ES_RunLoop(uint32_t* RunStatus) {
    (void)RunStatus;
    static uint32_t iterations = 0;
    iterations++;
    if (iterations > 5) {
        g_cFS_Running = 0U;
    }
    return g_cFS_Running;
}

void CFE_ES_RestartApp(uint32_t Reason) {
    CFE_EVS_SendEvent(ASTOS_ERR_EID, 3U, 
                      "[FATAL ERROR] Emergency Application Restart initiated. Reason Code: %d", Reason);
    g_cFS_Running = 0U; /* Exit flight loops */
}

/*
 * ==============================================================================
 * Core Application Lifecycle
 * ==============================================================================
 */

int32_t ASTOS_AppInit(void) {
    int32_t status;
    uint32_t RunStatus = 0;

    /* Initialize Application state memory */
    memset(&g_ASTOS_AppData, 0, sizeof(ASTOS_AppData_t));
    
    g_ASTOS_AppData.CmdCounter = 0U;
    g_ASTOS_AppData.ErrCounter = 0U;
    g_ASTOS_AppData.CalibratedEmissivity = 0.85f;
    g_ASTOS_AppData.EkfState = 0.85f;
    g_ASTOS_AppData.EkfCovariance = 0.1f;
    g_ASTOS_AppData.EkfProcessNoise = 0.001f;
    g_ASTOS_AppData.EkfSensorNoise = 0.05f;
    g_ASTOS_AppData.ControlMode = ASTOS_CONTROL_MODE_PID;
    
    /* Set stack baseline boundary address */
    g_ASTOS_AppData.StackBaseAddress = (uintptr_t)&RunStatus;

    /* Initialize Hamming and SHA-256 baseline memory structures */
    ASTOS_InitializeMemoryProtection();

    /* 1. Register with cFS Executive Services */
    status = CFE_ES_RegisterApp();
    if (status != 0) return status;

    /* 2. Register filters with Event Services */
    status = CFE_EVS_Register(NULL, 0, 0);
    if (status != 0) return status;

    /* 3. Create Software Bus Pipes */
    status = CFE_SB_CreatePipe(&g_ASTOS_AppData.CmdPipeId, ASTOS_PIPE_DEPTH, "ASTOS_CMD_PIPE");
    if (status != 0) return status;

    status = CFE_SB_CreatePipe(&g_ASTOS_AppData.TlmPipeId, ASTOS_PIPE_DEPTH, "ASTOS_TLM_PIPE");
    if (status != 0) return status;

    /* 4. Subscribe to Command and Telemetry Message IDs */
    CFE_SB_Subscribe(0x1801U, g_ASTOS_AppData.CmdPipeId); /* Sub to Cmds */
    CFE_SB_Subscribe(0x0801U, g_ASTOS_AppData.TlmPipeId); /* Sub to Sensors */

    /* 5. Register Parametric Thermal Tables */
    status = CFE_TBL_Register(&g_ASTOS_AppData.TableHandle, "ASTOS_ConfigTable", 
                              sizeof(ASTOS_ThermalTable_t), 0, NULL);
    if (status != 0) return status;

    /* Load initial table pointer address */
    CFE_TBL_GetAddress((void**)&g_ASTOS_AppData.ThermalTablePtr, g_ASTOS_AppData.TableHandle);

    CFE_EVS_SendEvent(ASTOS_INIT_INF_EID, 1U, "Spacecraft Thermal OS Onboard App initialized successfully.");
    return 0;
}

void ASTOS_AppMain(void) {
    uint32_t RunStatus = 0;
    int32_t status;
    
    status = ASTOS_AppInit();
    if (status != 0) {
        printf("Application initialization failed.\n");
        return;
    }

    /* Core Flight Software task loop execution */
    while (CFE_ES_RunLoop(&RunStatus)) {
        CFE_SB_Msg_t* MsgPtr = NULL;
        
        // Simulating Telemetry loop ingestion
        static int cycle = 0;
        cycle++;
        
        if (cycle % 2 == 0) {
            /* Create mock sensor telemetry incoming message */
            CFE_SB_Msg_t tlm_msg;
            tlm_msg.hdr[0] = 0x08; /* Message ID: 0x0801 */
            tlm_msg.hdr[1] = 0x01;
            ASTOS_ProcessTelemetryPacket(&tlm_msg);
        } else {
            /* Create mock command input message */
            CFE_SB_Msg_t cmd_msg;
            cmd_msg.hdr[0] = 0x18; /* Message ID: 0x1801 */
            cmd_msg.hdr[1] = 0x01;
            cmd_msg.sec[0] = ASTOS_NOOP_CC; /* NOOP command code */
            ASTOS_ProcessCommandPacket(&cmd_msg);
        }
    }
    
    printf("[cFS ES] Application terminating task successfully.\n");
}

/*
 * ==============================================================================
 * Command Packet Ingestion & Routing
 * ==============================================================================
 */

void ASTOS_ProcessCommandPacket(const CFE_SB_Msg_t* MsgPtr) {
    uint16_t command_code = MsgPtr->sec[0];
    
    switch (command_code) {
        case ASTOS_NOOP_CC:
            g_ASTOS_AppData.CmdCounter++;
            CFE_EVS_SendEvent(ASTOS_COMMAND_INF_EID, 1U, 
                              "AST-OS cFS: Received NOOP command. Counters incremented (Val: %d).", 
                              g_ASTOS_AppData.CmdCounter);
            break;
            
        case ASTOS_RESET_CC:
            g_ASTOS_AppData.CmdCounter = 0U;
            g_ASTOS_AppData.ErrCounter = 0U;
            CFE_EVS_SendEvent(ASTOS_COMMAND_INF_EID, 1U, "AST-OS cFS: Resets command execution counters.");
            break;
            
        case ASTOS_SETPARAM_CC:
            {
                const ASTOS_SetParamCmd_t* cmd = (const ASTOS_SetParamCmd_t*)MsgPtr;
                if (cmd->CpuSafeLimit > 0.0f && g_ASTOS_AppData.ThermalTablePtr != NULL) {
                    g_ASTOS_AppData.ThermalTablePtr->MaxSafeTempLimit[0] = cmd->CpuSafeLimit;
                    g_ASTOS_AppData.CmdCounter++;
                    CFE_EVS_SendEvent(ASTOS_COMMAND_INF_EID, 1U, 
                                      "AST-OS cFS: Parameter updated. CPU safe boundary set to %.2f C.", 
                                      cmd->CpuSafeLimit);
                } else {
                    g_ASTOS_AppData.ErrCounter++;
                    CFE_EVS_SendEvent(ASTOS_ERR_EID, 3U, "AST-OS cFS: Command validation failed. Invalid limits.");
                }
            }
            break;
            
        case ASTOS_SET_MPC_MODE_CC:
            {
                /* Sets control modes: PID vs MPC */
                uint8_t mode = MsgPtr->sec[1];
                if (mode == ASTOS_CONTROL_MODE_PID || mode == ASTOS_CONTROL_MODE_MPC) {
                    g_ASTOS_AppData.ControlMode = mode;
                    g_ASTOS_AppData.CmdCounter++;
                    CFE_EVS_SendEvent(ASTOS_COMMAND_INF_EID, 1U, 
                                      "AST-OS cFS: Control mode updated successfully to %s.", 
                                      mode == ASTOS_CONTROL_MODE_MPC ? "MPC" : "PID");
                } else {
                    g_ASTOS_AppData.ErrCounter++;
                    CFE_EVS_SendEvent(ASTOS_ERR_EID, 3U, "AST-OS cFS: Command validation failed. Invalid mode.");
                }
            }
            break;
            
        default:
            g_ASTOS_AppData.ErrCounter++;
            CFE_EVS_SendEvent(ASTOS_ERR_EID, 3U, "AST-OS cFS: Received invalid command code: %d", command_code);
            break;
    }
}

/*
 * ==============================================================================
 * Telemetry Ingestion & Physics Core Inference (EKF + Model Predictive Control)
 * ==============================================================================
 */

void ASTOS_ProcessTelemetryPacket(const CFE_SB_Msg_t* MsgPtr) {
    (void)MsgPtr;
    
    /* Simulate loading dynamic external sensors values */
    static float power_dissipation = 15.0f;     /* Avionics CPU heat load in Watts */
    static float simulated_measured_temp = 54.0f;
    
    // Induce temporary radiator solar shadowing cycle
    simulated_measured_temp += 0.5f; 
    
    /* 1. Run online EKF State estimation to evaluate actual radiator emissivity */
    ASTOS_RunEfkStateEstimation(simulated_measured_temp, power_dissipation);
    
    /* 2. Run deterministic weights checks (EDAC + SHA-256) before inference */
    uint32_t corrections_made = 0;
    uint8_t active_bytes[RAW_WEIGHTS_SIZE];
    
    /* Decode active weights from RAM and execute 1-bit corrections */
    for (int32_t i = 0; i < RAW_WEIGHTS_SIZE; i++) {
        active_bytes[i] = hamming_decode_byte(&ACTIVE_RAM_ENCODED[2 * i], &corrections_made);
    }
    
    if (corrections_made > 0U) {
        CFE_EVS_SendEvent(ASTOS_EDAC_CORR_EID, 1U, 
                          "EDAC: Hamming(7,4) detected and corrected %d single-bit memory corruptions.", 
                          corrections_made);
    }
    
    /* Integrity verification: Calculate SHA-256 */
    uint8_t current_hash[32];
    ASTOS_SHA256_Ctx_t sha_ctx;
    ASTOS_SHA256_Init(&sha_ctx);
    ASTOS_SHA256_Update(&sha_ctx, active_bytes, RAW_WEIGHTS_SIZE);
    ASTOS_SHA256_Final(&sha_ctx, current_hash);
    
    if (memcmp(current_hash, GOLDEN_HASH_SHA256, 32) != 0) {
        /* Multi-bit error or severe corruption! Invalidate and reload from Golden Copy */
        CFE_EVS_SendEvent(ASTOS_INTEG_FAIL_EID, 2U, 
                          "CRITICAL: SHA-256 hash mismatch! Memory segment corrupted. Reloading Golden Copy.");
        
        memcpy(ACTIVE_RAM_ENCODED, GOLDEN_WEIGHTS_ENCODED, ENCODED_WEIGHTS_SIZE);
        memcpy(active_bytes, GOLDEN_WEIGHTS_FLOAT, RAW_WEIGHTS_SIZE);
        
        CFE_EVS_SendEvent(ASTOS_INTEG_RELOAD_EID, 1U, 
                          "RECOVERY: Neural surrogate weights successfully restored from Flash.");
    }
    
    /* Map cleaned raw bytes back to global floats */
    memcpy(g_Active_FC1_WEIGHTS, &active_bytes[0], 16);
    memcpy(g_Active_FC1_BIASES, &active_bytes[16], 16);
    memcpy(g_Active_FC2_WEIGHTS, &active_bytes[32], 32);
    memcpy(g_Active_FC2_BIASES, &active_bytes[64], 8);
    
    /* 3. Run control solvers based on the active mode (Classical vs MPC) */
    float mpc_opt_q = power_dissipation;
    float mpc_opt_eps = g_ASTOS_AppData.CalibratedEmissivity;
    
    if (g_ASTOS_AppData.ControlMode == ASTOS_CONTROL_MODE_MPC) {
        /* Run Model Predictive Control solver */
        ASTOS_SolveMPC(simulated_measured_temp, g_ASTOS_AppData.CalibratedEmissivity, &mpc_opt_q, &mpc_opt_eps);
        
        /* Apply MPC optimal power and louver control states */
        power_dissipation = mpc_opt_q;
        g_ASTOS_AppData.CalibratedEmissivity = mpc_opt_eps;
    }
    
    /* 4. Run deterministic MLP neural surrogate model to forecast next step bounds */
    float inference_input[1] = { power_dissipation };
    float inference_output[2] = { 0.0f, 0.0f }; /* Predicted CPU Temp, time to critical */
    
    ASTOS_RunThermalInference(inference_input, inference_output);
    
    g_ASTOS_AppData.PredictedCpuMax = inference_output[0];
    g_ASTOS_AppData.TimeToCritical = inference_output[1];
    
    /* Update running telemetry channels */
    g_ASTOS_AppData.NodeTemps[0] = simulated_measured_temp;
    g_ASTOS_AppData.NodeTemps[1] = 23.4f; /* Mock EPS Battery */
    g_ASTOS_AppData.NodeTemps[2] = 31.8f; /* Mock Payload Optics */
    g_ASTOS_AppData.NodeTemps[3] = 43.6f; /* Mock Structure */
    g_ASTOS_AppData.NodeTemps[4] = 37.1f; /* Mock Radiator Node */
    
    /* 5. Evaluate FDIR countermeasure boundaries */
    ASTOS_TriggerFdirCountermeasures();
    
    /* 6. Compile CCSDS telemetry output packet and send to Software Bus */
    g_ASTOS_AppData.OutTlmPacket.CpuTemperature = g_ASTOS_AppData.NodeTemps[0];
    g_ASTOS_AppData.OutTlmPacket.BatteryTemperature = g_ASTOS_AppData.NodeTemps[1];
    g_ASTOS_AppData.OutTlmPacket.PayloadTemperature = g_ASTOS_AppData.NodeTemps[2];
    g_ASTOS_AppData.OutTlmPacket.StructureTemperature = g_ASTOS_AppData.NodeTemps[3];
    g_ASTOS_AppData.OutTlmPacket.RadiatorTemperature = g_ASTOS_AppData.NodeTemps[4];
    
    g_ASTOS_AppData.OutTlmPacket.PredictedCpuMaxTemp = g_ASTOS_AppData.PredictedCpuMax;
    g_ASTOS_AppData.OutTlmPacket.CalibratedEmissivity = g_ASTOS_AppData.CalibratedEmissivity;
    g_ASTOS_AppData.OutTlmPacket.TimeToCritical = g_ASTOS_AppData.TimeToCritical;
    g_ASTOS_AppData.OutTlmPacket.FdirActiveFlag = g_ASTOS_AppData.FdirActive;
    g_ASTOS_AppData.OutTlmPacket.RedundantEkfActive = g_ASTOS_AppData.RedundantEkfActive;
    
    CFE_SB_SendMsg((CFE_SB_Msg_t*)&g_ASTOS_AppData.OutTlmPacket);
    
    CFE_EVS_SendEvent(ASTOS_TLM_INF_EID, 1U, 
                      "Telemetry Ingested: CPU = %.2f C | Mode: %s | Optimal Q_cpu: %.1f W | Predicted T_max = %.2f C",
                      g_ASTOS_AppData.NodeTemps[0], 
                      g_ASTOS_AppData.ControlMode == ASTOS_CONTROL_MODE_MPC ? "MPC" : "PID/Classical",
                      power_dissipation, g_ASTOS_AppData.PredictedCpuMax);
}

/*
 * ==============================================================================
 * Physics Core: Deterministic EKF Parameter Calibration Step
 * ==============================================================================
 */

void ASTOS_RunEfkStateEstimation(float observed_temp, float input_power) {
    float predicted_temp;
    float measurement_residual;
    float observation_jacobian;
    float kalman_gain;
    
    float sigma_const = 5.67e-8f;
    float area = 0.15f;
    
    if (g_ASTOS_AppData.ThermalTablePtr != NULL) {
        area = g_ASTOS_AppData.ThermalTablePtr->Area[4];
    }
    
    /* Division by Zero Check (MISRA exception safety check) */
    float denominator_predict = g_ASTOS_AppData.EkfState * sigma_const * area;
    if (fabs(denominator_predict) < 1e-12f) {
        CFE_EVS_SendEvent(ASTOS_ERR_EID, 3U, "EXC: Div by Zero blocked in EKF prediction updates.");
        return; /* Skip step to prevent NaNs */
    }
    
    /* Time Update (Predict State) */
    float prior_state = g_ASTOS_AppData.EkfState;
    float prior_cov = g_ASTOS_AppData.EkfCovariance + g_ASTOS_AppData.EkfProcessNoise;
    
    /* Measurement prediction */
    predicted_temp = (input_power / denominator_predict);
    predicted_temp = powf(predicted_temp, 0.25f) - 273.15f; /* Convert Kelvin to Celsius */
    
    /* Observation Jacobian H = d(Temp)/d(eps) */
    observation_jacobian = -predicted_temp / (4.0f * prior_state + 1e-6f);
    
    /* Measurement Update (Correct State) */
    measurement_residual = observed_temp - predicted_temp;
    
    float s_matrix = (observation_jacobian * prior_cov * observation_jacobian) + g_ASTOS_AppData.EkfSensorNoise;
    
    /* Division by Zero check in Kalman Gain calculations */
    if (fabs(s_matrix) < 1e-6f) {
        CFE_EVS_SendEvent(ASTOS_ERR_EID, 3U, "EXC: Div by Zero blocked in Kalman Gain denominator updates.");
        return;
    }
    
    kalman_gain = (prior_cov * observation_jacobian) / s_matrix;
    
    g_ASTOS_AppData.EkfState = prior_state + kalman_gain * measurement_residual;
    g_ASTOS_AppData.EkfCovariance = (1.0f - kalman_gain * observation_jacobian) * prior_cov;
    
    /* Enforce physics-based bounds [0.05, 0.95] */
    if (g_ASTOS_AppData.EkfState < 0.05f) g_ASTOS_AppData.EkfState = 0.05f;
    if (g_ASTOS_AppData.EkfState > 0.95f) g_ASTOS_AppData.EkfState = 0.95f;
    
    g_ASTOS_AppData.CalibratedEmissivity = g_ASTOS_AppData.EkfState;
}

/*
 * ==============================================================================
 * Physics Core: Deterministic 3-Layer MLP Surrogate Inference
 * Input: CPU internal heat power (Watts)
 * Output: predicted temperatures (Celsius), time to critical boundary (seconds)
 * ==============================================================================
 */

#define FC1_IN   1
#define FC1_OUT  4
#define FC2_OUT  2

void ASTOS_RunThermalInference(const float input_power[1], float output_temps[2]) {
    float hidden[FC1_OUT];
    int32_t i;
    int32_t j;
    
    /* Exception Check: Stack Overflow */
    uintptr_t current_sp = (uintptr_t)&current_sp;
    ptrdiff_t stack_depth = (ptrdiff_t)(g_ASTOS_AppData.StackBaseAddress - current_sp);
    if (stack_depth < 0) stack_depth = -stack_depth;
    
    if (stack_depth > 8192) {
        CFE_ES_RestartApp(1U); /* Code 1: Stack Overflow Exception */
        return;
    }
    
    /* Exception Check: Task Execution Timeout */
    /* wc_cycles acts as a virtual cycle watchdog clock */
    static uint32_t wc_cycles = 0;
    wc_cycles++;
    if (wc_cycles > 500) {
        /* Task exceeds virtual watch dog 2x WCET limit */
        CFE_ES_RestartApp(2U); /* Code 2: CPU Execution Timeout */
        wc_cycles = 0;
        return;
    }
    
    /* FC1 + ReLU Activation using verified corrected active weight segments */
    for (i = 0; i < FC1_OUT; i++) {
        float sum = g_Active_FC1_BIASES[i];
        for (j = 0; j < FC1_IN; j++) {
            sum += g_Active_FC1_WEIGHTS[i][j] * input_power[j];
        }
        
        /* ReLU logic with Division safety checks if needed */
        hidden[i] = sum > 0.0f ? sum : 0.0f;
    }
    
    /* FC2 Output layer */
    for (i = 0; i < FC2_OUT; i++) {
        float sum = g_Active_FC2_BIASES[i];
        for (j = 0; j < FC1_OUT; j++) {
            sum += g_Active_FC2_WEIGHTS[i][j] * hidden[j];
        }
        output_temps[i] = sum;
    }
    
    /* Rescale outputs: Output[0] is CPU Temp predicted peak, Output[1] is time-to-critical */
    output_temps[0] = 50.0f + 1.25f * output_temps[0]; /* Denormalize CPU peak temperature */
    output_temps[1] = output_temps[1] > 0.0f ? (100.0f * output_temps[1]) : -1.0f; /* Denormalize time */
}

/*
 * ==============================================================================
 * Onboard FDIR Event-Triggered Countermeasures
 * ==============================================================================
 */

void ASTOS_TriggerFdirCountermeasures(void) {
    float cpu_safe_limit = 85.0f;
    
    if (g_ASTOS_AppData.ThermalTablePtr != NULL) {
        cpu_safe_limit = g_ASTOS_AppData.ThermalTablePtr->MaxSafeTempLimit[0];
    }
    
    /* Evaluate safe margin */
    if (g_ASTOS_AppData.NodeTemps[0] >= cpu_safe_limit) {
        if (g_ASTOS_AppData.FdirActive == 0U) {
            g_ASTOS_AppData.FdirActive = 1U;
            CFE_EVS_SendEvent(ASTOS_FDIR_WARN_EID, 2U, 
                              "CRITICAL FAULT: CPU Temp (%.2f C) exceeds safe boundary (%.1f C)! FDIR Throttling active.",
                              g_ASTOS_AppData.NodeTemps[0], cpu_safe_limit);
        }
    } else {
        if (g_ASTOS_AppData.FdirActive == 1U && g_ASTOS_AppData.NodeTemps[0] < (cpu_safe_limit - 5.0f)) {
            /* Deactivate throttling once thermal hysterisis recovery threshold is crossed */
            g_ASTOS_AppData.FdirActive = 0U;
            CFE_EVS_SendEvent(ASTOS_FDIR_RECOVERY_EID, 1U, 
                              "RECOVERY COMPLETED: CPU Temp (%.2f C) returned inside nominal envelopes. Resuming operations.",
                              g_ASTOS_AppData.NodeTemps[0]);
        }
    }
}

#ifndef UNIT_TESTING
/* Standalone main execution wrapper */
int main(void) {
    printf("==============================================================================\n");
    printf("            AST-OS NASA cFS Onboard Application Simulation Cockpit\n");
    printf("==============================================================================\n");
    
    ASTOS_AppMain();
    
    printf("==============================================================================\n");
    printf("                  cFS Simulation Executed Successfully\n");
    printf("==============================================================================\n");
    return 0;
}
#endif
